# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
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

"""Rockcraft Package service."""

import datetime
import pathlib
import typing
from collections.abc import Mapping
from typing import cast

from craft_application import PackageService, errors, models
from craft_cli import emit
from typing_extensions import override

from rockcraft import oci
from rockcraft.models import Project
from rockcraft.pebble import Pebble
from rockcraft.services.image import RockcraftImageService
from rockcraft.usernames import SUPPORTED_GLOBAL_USERNAMES
from rockcraft.utils import parse_command


class RockcraftPackageService(PackageService):
    """Package service subclass for Rockcraft."""

    @override
    def get_artifacts(self) -> dict[str | None, pathlib.Path]:
        """Get the output artifacts for this application.

        Returns a single default artifact path based on the project name,
        version, and platform.
        """
        project = cast(Project, self._services.get("project").get())
        build_plan = self._services.get("build_plan").plan()

        if len(build_plan) > 1:
            raise errors.MultipleBuildsError

        platform = build_plan[0].platform
        archive_name = f"{project.name}_{project.version}_{platform}.rock"
        return {None: self.output_dir / archive_name}

    @override
    def _pack(self, *, name: str | None = None, path: pathlib.Path) -> None:
        """Pack a specific artifact for the rock.

        :param name: The artifact name (always None for single-artifact).
        :param path: The output path for the .rock artifact.
        """
        if name is not None:
            raise ValueError(
                f"Rockcraft only supports a single unnamed artifact, got name={name!r}"
            )

        image_service = cast(RockcraftImageService, self._services.get("image"))
        image_info = image_service.obtain_image()

        lifecycle = self._services.get("lifecycle")
        prime_dir = lifecycle.prime_dir

        build_plan = self._services.get("build_plan").plan()
        build_for = build_plan[0].build_for

        _create_rock(
            path=path,
            prime_dir=prime_dir,
            project=cast(Project, self._services.get("project").get()),
            project_base_image=image_info.base_image,
            base_digest=image_info.base_digest,
            build_for=build_for,
            base_layer_dir=image_info.base_layer_dir,
        )

    @override
    def write_metadata(self, path: pathlib.Path) -> None:
        """Write the project metadata to metadata.yaml in the given directory.

        :param path: The path to the prime directory.
        """
        # nop (no metadata file for Rockcraft)

    @override
    def write_artifacts_state(
        self, artifacts: Mapping[str | None, pathlib.Path]
    ) -> None:
        """Write artifact-oriented packaging state.

        Rockcraft's pack flow rewrites artifact state on every run, including
        the "already packed" skip path enabled by ``always_repack=False``. The
        base implementation refuses to replace an existing entry, so we override
        it to pass ``overwrite=True``.
        """
        platform = self._build_info.platform
        state_service = self._services.get("state")
        state_entries = [
            {"name": name, "path": str(path)} for name, path in artifacts.items()
        ]

        state_service.set(
            "artifacts", platform, value=state_entries or None, overwrite=True
        )

    @property
    def metadata(self) -> models.BaseMetadata:
        """Get the metadata model for this project."""
        # nop (no metadata file for Rockcraft)
        return models.BaseMetadata()


def _create_rock(
    *,
    path: pathlib.Path,
    prime_dir: pathlib.Path,
    project: Project,
    project_base_image: oci.Image,
    base_digest: bytes,
    build_for: str,
    base_layer_dir: pathlib.Path,
) -> None:
    """Create the rock image for a given architecture.

    :param path:
      The output path for the .rock artifact.
    :param prime_dir:
      The directory containing the primed payload for the rock.
    :param project:
      The project model with configuration for the rock.
    :param project_base_image:
      The Image for the base over which the payload was primed.
    :param base_digest:
      The digest of the base image, to add to the new image's metadata.
    :param build_for:
      The architecture of the built rock, to add as metadata.
    :param base_layer_dir:
      The directory where the rock's base image was extracted.
    """
    emit.progress("Creating new layer")

    # At this point the version must be set, otherwise it would have failed earlier.
    version = cast(str, project.version)

    new_image = project_base_image.add_layer(
        tag=version,
        new_layer_dir=prime_dir,
        base_layer_dir=base_layer_dir,
    )
    emit.progress("Created new layer")
    if project.run_user:
        emit.progress(f"Creating new user {project.run_user}")
        userid = SUPPORTED_GLOBAL_USERNAMES[project.run_user]["uid"]
        new_image.add_user(
            prime_dir=prime_dir,
            base_layer_dir=base_layer_dir,
            tag=version,
            username=project.run_user,
            uid=userid,
        )

        emit.progress(f"Setting the default OCI user to be {project.run_user}")
        new_image.set_default_user(userid, project.run_user)

    if project.entrypoint_command:
        emit.progress("Setting OCI entrypoint")
        entrypoint, cmd = parse_command(project.entrypoint_command)
    else:
        emit.progress("Adding Pebble entrypoint")

        entrypoint = Pebble.get_entrypoint(project.build_base or project.base)
        cmd = []

        if project.entrypoint_service:
            entrypoint.extend(["--args", project.entrypoint_service])

        if project.services and project.entrypoint_service in project.services:
            command = project.services[project.entrypoint_service].command
            cmd = parse_command(command or "")[1]

    new_image.set_entrypoint(entrypoint)
    new_image.set_cmd(cmd)
    new_image.set_default_path(project.base)

    dumped = project.marshal()
    services = cast(dict[str, typing.Any], dumped.get("services", {}))
    checks = cast(dict[str, typing.Any], dumped.get("checks", {}))

    if services or checks:
        new_image.set_pebble_layer(
            services=services,
            checks=checks,
            name=project.name,
            tag=version,
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
        datetime.datetime.now(datetime.timezone.utc).isoformat(), base_digest, build_for
    )
    new_image.set_annotations(oci_annotations)
    new_image.set_control_data(rock_metadata)
    emit.progress("Metadata added")

    # Set the media type in the target images's manifest.
    # This is different than calling _inject_oci_fields in oci.Image.new_oci_image,
    # since _inject_oci_fields is called in the context of creating the base image.
    emit.progress("Adding manifest media type")
    new_image.set_media_type(arch=build_for)
    emit.progress("Manifest media type added")

    emit.progress("Exporting to OCI archive")
    new_image.to_oci_archive(tag=version, filename=str(path))
    emit.progress(f"Exported to OCI archive '{path.name}'")
