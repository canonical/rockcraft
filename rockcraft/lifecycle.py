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

from craft_cli import EmitterMode, emit

from . import oci, providers, utils
from .parts import PartsLifecycle, Step
from .project import Project, load_project
from .providers import capture_logs_from_instance


def pack():
    """Pack a ROCK."""
    project = load_project("rockcraft.yaml")
    destructive_mode = False  # XXX: obtain from command line

    managed_mode = utils.is_managed_mode()
    if not managed_mode and not destructive_mode:
        pack_in_provider(project)
        return

    if managed_mode:
        work_dir = utils.get_managed_environment_home_path()
    else:
        work_dir = Path("work").absolute()

    image_dir = work_dir / "images"
    bundle_dir = work_dir / "bundles"

    # Obtain base image and extract it to use as our overlay base
    # TODO: check if image was already downloaded, etc.
    emit.progress(f"Retrieving base {project.base}")
    if project.base == "bare":
        base_image = oci.Image.new_oci_image(image_dir=image_dir)
    else:
        base_image = oci.Image.from_docker_registry(project.base, image_dir=image_dir)
    emit.message(f"Retrieved base {project.base}", intermediate=True)

    emit.progress(f"Extracting {base_image.image_name}")
    rootfs = base_image.extract_to(bundle_dir)
    emit.message(f"Extracted {base_image.image_name}", intermediate=True)

    # TODO: check if destination image already exists, etc.
    project_base_image = base_image.copy_to(
        f"{project.name}:rockcraft-base", image_dir=image_dir
    )

    lifecycle = PartsLifecycle(
        project.parts,
        work_dir=work_dir,
        base_layer_dir=rootfs,
        base_layer_hash=project_base_image.digest(),
    )
    lifecycle.run(Step.PRIME)

    emit.progress("Creating new layer")
    new_image = project_base_image.add_layer(
        tag=project.version, layer_path=lifecycle.prime_dir
    )
    emit.message("Created new layer", intermediate=True)

    if project.entrypoint:
        new_image.set_entrypoint(project.entrypoint)
        if not project.cmd:
            new_image.set_cmd([])

    if project.cmd:
        new_image.set_cmd(project.cmd)

    if project.env:
        new_image.set_env(project.env)

    # Set annotations and metadata, both dynamic and the ones based on user-provided properties
    # Also include the "created" timestamp, just before packing the image
    emit.progress("Adding metadata")
    packing_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    oci_annotations, rock_metadata = project.generate_project_metadata(packing_time)
    new_image.set_annotations(oci_annotations)
    new_image.set_control_data(rock_metadata)
    emit.progress("Metadata added")

    emit.progress("Exporting to OCI archive")
    archive_name = f"{project.name}_{project.version}.rock"
    new_image.to_oci_archive(tag=project.version, filename=archive_name)
    emit.message(f"Exported to OCI archive '{archive_name}'", intermediate=True)


def pack_in_provider(project: Project):
    """Pack image in provider instance."""
    provider = providers.get_provider()
    provider.ensure_provider_is_available()

    cmd = ["rockcraft", "pack"]

    if emit.get_mode() == EmitterMode.VERBOSE:
        cmd.append("--verbose")
    elif emit.get_mode() == EmitterMode.QUIET:
        cmd.append("--quiet")
    elif emit.get_mode() == EmitterMode.TRACE:
        cmd.append("--trace")

    output_dir = utils.get_managed_environment_project_path()

    emit.progress("Launching instance...")
    with provider.launched_environment(
        project_name=project.name,
        project_path=Path().absolute(),
        build_base=str(project.build_base),
    ) as instance:
        try:
            with emit.pause():
                instance.execute_run(cmd, check=True, cwd=output_dir)
            capture_logs_from_instance(instance)
        except subprocess.CalledProcessError as err:
            capture_logs_from_instance(instance)
            raise providers.ProviderError(
                f"Failed to pack image '{project.name}:{project.version}'."
            ) from err
