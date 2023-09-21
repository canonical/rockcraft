# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021-2022 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Lifecycle integration."""

import datetime
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

from craft_cli import emit
from craft_parts import ProjectDirs, ProjectInfo, expand_environment
from craft_providers import ProviderError

from . import oci, providers, utils
from .models.project import Project, load_project
from .parts import PartsLifecycle
from .usernames import SUPPORTED_GLOBAL_USERNAMES

if TYPE_CHECKING:
    import argparse


def run(command_name: str, parsed_args: "argparse.Namespace") -> None:
    """Run the parts lifecycle."""
    # pylint: disable=too-many-locals
    emit.trace(f"command: {command_name}, arguments: {parsed_args}")

    project_yaml = load_project(Path("rockcraft.yaml"))
    destructive_mode = getattr(parsed_args, "destructive_mode", False)

    part_names = getattr(parsed_args, "parts", None)
    managed_mode = utils.is_managed_mode()

    if not managed_mode and not destructive_mode:
        if command_name == "clean" and not part_names:
            clean_provider(
                project_name=project_yaml["name"], project_path=Path().absolute()
            )
        else:
            run_in_provider(Project.unmarshal(project_yaml), command_name, parsed_args)
        return

    if managed_mode:
        work_dir = utils.get_managed_environment_home_path()
    else:
        work_dir = Path().absolute()

    project_vars = {"version": project_yaml["version"]}
    # Expand the environment so that the global variables can be interpolated
    _expand_environment(
        project_yaml,
        project_vars=project_vars,
        work_dir=work_dir,
    )

    # pylint: disable=no-member
    project = Project.unmarshal(project_yaml)

    image_dir = work_dir / "images"
    bundle_dir = work_dir / "bundles"

    if project.package_repositories is None:
        package_repositories = []
    else:
        package_repositories = project.package_repositories

    # Obtain base image and extract it to use as our overlay base
    # TODO: check if image was already downloaded, etc.
    emit.progress(f"Retrieving base {project.base}")

    for platform_entry, platform in project.platforms.items():
        build_for = (
            platform["build_for"][0] if platform.get("build_for") else platform_entry
        )
        build_for_variant = platform.get("build_for_variant")

        if project.base == "bare":
            base_image, source_image = oci.Image.new_oci_image(
                f"{project.base}:latest",
                image_dir=image_dir,
                arch=build_for,
                variant=build_for_variant,
            )
        else:
            base_image, source_image = oci.Image.from_docker_registry(
                project.base,
                image_dir=image_dir,
                arch=build_for,
                variant=build_for_variant,
            )
        emit.progress(f"Retrieved base {project.base} for {build_for}", permanent=True)

        emit.progress(f"Extracting {base_image.image_name}")
        rootfs = base_image.extract_to(bundle_dir)
        emit.progress(f"Extracted {base_image.image_name}", permanent=True)

        # TODO: check if destination image already exists, etc.
        project_base_image = base_image.copy_to(
            f"{project.name}:rockcraft-base", image_dir=image_dir
        )

        base_digest = project_base_image.digest(source_image)
        step_name = "prime" if command_name == "pack" else command_name

        lifecycle = PartsLifecycle(
            project.parts,
            project_name=project.name,
            project_vars=project_vars,
            work_dir=work_dir,
            part_names=part_names,
            base_layer_dir=rootfs,
            base_layer_hash=base_digest,
            base=project.base,
            package_repositories=package_repositories,
        )

        if command_name == "clean":
            lifecycle.clean()
            return

        lifecycle.run(
            step_name,
            shell=getattr(parsed_args, "shell", False),
            shell_after=getattr(parsed_args, "shell_after", False),
            debug=getattr(parsed_args, "debug", False),
        )

        if command_name == "pack":
            _pack(
                prime_dir=lifecycle.prime_dir,
                project=project,
                project_base_image=project_base_image,
                base_digest=base_digest,
                rock_suffix=platform_entry,
                build_for=build_for,
                base_layer_dir=rootfs,
            )


def _pack(
    *,
    prime_dir: Path,
    project: Project,
    project_base_image: oci.Image,
    base_digest: bytes,
    rock_suffix: str,
    build_for: str,
    base_layer_dir: Path,
) -> str:
    """Create the rock image for a given architecture.

    :param lifecycle:
      The lifecycle object containing the primed payload for the rock.
    :param project_base_image:
      The Image for the base over which the payload was primed.
    :param base_digest:
      The digest of the base image, to add to the new image's metadata.
    :param rock_suffix:
      The suffix to append to the image's filename, after the name and version.
    :param build_for:
      The architecture of the built rock, to add as metadata.
    :param base_layer_dir:
      The directory where the rock's base image was extracted.
    """
    emit.progress("Creating new layer")
    new_image = project_base_image.add_layer(
        tag=project.version,
        new_layer_dir=prime_dir,
        base_layer_dir=base_layer_dir,
    )
    emit.progress("Created new layer")

    if project.run_user:
        emit.progress(f"Creating new user {project.run_user}")
        new_image.add_user(
            prime_dir=prime_dir,
            base_layer_dir=base_layer_dir,
            tag=project.version,
            username=project.run_user,
            uid=SUPPORTED_GLOBAL_USERNAMES[project.run_user]["uid"],
        )

        emit.progress(f"Setting the default OCI user to be {project.run_user}")
        new_image.set_default_user(project.run_user)

    emit.progress("Adding Pebble entrypoint")

    new_image.set_entrypoint()

    services = project.dict(exclude_none=True, by_alias=True).get("services", {})

    checks = project.dict(exclude_none=True, by_alias=True).get("checks", {})

    if services or checks:
        new_image.set_pebble_layer(
            services=services,
            checks=checks,
            name=project.name,
            tag=project.version,
            summary=project.summary,
            description=project.description,
            base_layer_dir=base_layer_dir,
        )

    if project.environment:
        new_image.set_environment(project.environment)

    # Set annotations and metadata, both dynamic and the ones based on user-provided properties
    # Also include the "created" timestamp, just before packing the image
    emit.progress("Adding metadata")
    oci_annotations, rock_metadata = project.generate_metadata(
        datetime.datetime.now(datetime.timezone.utc).isoformat(), base_digest
    )
    rock_metadata["architecture"] = build_for
    # TODO: add variant to rock_metadata too
    # if build_for_variant:
    #     rock_metadata["variant"] = build_for_variant
    new_image.set_annotations(oci_annotations)
    new_image.set_control_data(rock_metadata)
    emit.progress("Metadata added")

    emit.progress("Exporting to OCI archive")
    archive_name = f"{project.name}_{project.version}_{rock_suffix}.rock"
    new_image.to_oci_archive(tag=project.version, filename=archive_name)
    emit.progress(f"Exported to OCI archive '{archive_name}'", permanent=True)

    return archive_name


def run_in_provider(
    project: Project, command_name: str, parsed_args: "argparse.Namespace"
) -> None:
    """Run lifecycle command in provider instance."""
    provider = providers.get_provider()
    providers.ensure_provider_is_available(provider)

    cmd = ["rockcraft", command_name]

    if hasattr(parsed_args, "parts"):
        cmd.extend(parsed_args.parts)

    mode = emit.get_mode().name.lower()
    cmd.append(f"--verbosity={mode}")

    if getattr(parsed_args, "shell", False):
        cmd.append("--shell")
    if getattr(parsed_args, "shell_after", False):
        cmd.append("--shell-after")
    if getattr(parsed_args, "debug", False):
        cmd.append("--debug")

    host_project_path = Path().absolute()
    instance_project_path = utils.get_managed_environment_project_path()
    instance_name = providers.get_instance_name(
        project_name=project.name, project_path=host_project_path
    )
    build_base = providers.ROCKCRAFT_BASE_TO_PROVIDER_BASE[str(project.build_base)]

    base_configuration = providers.get_base_configuration(
        alias=build_base,
        project_name=project.name,
        project_path=host_project_path,
    )

    emit.progress("Launching instance...")
    with provider.launched_environment(
        project_name=project.name,
        project_path=host_project_path,
        base_configuration=base_configuration,
        instance_name=instance_name,
    ) as instance:
        try:
            with emit.pause():
                instance.mount(
                    host_source=host_project_path, target=instance_project_path
                )
                instance.execute_run(cmd, check=True, cwd=instance_project_path)
        except subprocess.CalledProcessError as err:
            raise ProviderError(
                f"Failed to execute {command_name} in instance."
            ) from err
        finally:
            providers.capture_logs_from_instance(instance)


def clean_provider(project_name: str, project_path: Path) -> None:
    """Clean the provider environment.

    :param project_name: name of the project
    :param project_path: path of the project
    """
    emit.progress("Cleaning build provider")
    provider = providers.get_provider()
    instance_name = providers.get_instance_name(
        project_name=project_name, project_path=project_path
    )
    emit.debug(f"Cleaning instance {instance_name}")
    provider.clean_project_environments(instance_name=instance_name)
    emit.progress("Cleaned build provider", permanent=True)


def _set_global_environment(info: ProjectInfo) -> None:
    """Set global environment variables."""
    info.global_environment.update(
        {
            "CRAFT_PROJECT_VERSION": info.get_project_var("version", raw_read=True),
        }
    )


def _expand_environment(
    project_yaml: Dict[str, Any],
    *,
    project_vars: Dict[str, Any],
    work_dir: Path,
) -> None:
    """Expand global variables in the provided dictionary values.

    :param project_yaml: A dictionary containing the rockcraft.yaml's contents.
    :param project_var: A dictionary with the project-specific variables.
    :param work_dir: The working directory.
    """
    info = ProjectInfo(
        application_name="rockcraft",  # not used in environment expansion
        cache_dir=Path(),  # not used in environment expansion
        project_name=project_yaml.get("name", ""),
        project_dirs=ProjectDirs(work_dir=work_dir),
        project_vars=project_vars,
    )
    _set_global_environment(info)

    expand_environment(project_yaml, info=info)
