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
from typing import cast

from craft_application import PackageService, errors, models
from craft_cli import emit
from overrides import override  # type: ignore[reportUnknownVariableType]

from rockcraft import oci
from rockcraft.models import Project
from rockcraft.pebble import Pebble
from rockcraft.usernames import SUPPORTED_GLOBAL_USERNAMES
from rockcraft.utils import parse_command


class RockcraftPackageService(PackageService):
    """Package service subclass for Rockcraft."""

    @override
    def pack(self, prime_dir: pathlib.Path, dest: pathlib.Path) -> list[pathlib.Path]:
        """Create one or more packages as appropriate.

        :param dest: Directory into which to write the package(s).
        :returns: A list of paths to created packages.
        """
        # This inner import is necessary to resolve a cyclic import
        # pylint: disable=import-outside-toplevel
        from rockcraft.services import RockcraftImageService

        image_service = cast(RockcraftImageService, self._services.get("image"))
        image_info = image_service.obtain_image()

        build_plan = self._services.get("build_plan").plan()

        if len(build_plan) > 1:
            raise errors.MultipleBuildsError

        platform = build_plan[0].platform
        build_for = build_plan[0].build_for

        archive_name = _pack(
            prime_dir=prime_dir,
            project=cast(Project, self._services.get("project").get()),
            project_base_image=image_info.base_image,
            base_digest=image_info.base_digest,
            rock_suffix=platform,
            build_for=build_for,
            base_layer_dir=image_info.base_layer_dir,
        )

        return [dest / archive_name]

    @override
    def write_metadata(self, path: pathlib.Path) -> None:
        """Write the project metadata to metadata.yaml in the given directory.

        :param path: The path to the prime directory.
        """
        # nop (no metadata file for Rockcraft)

    @property
    def metadata(self) -> models.BaseMetadata:
        """Get the metadata model for this project."""
        # nop (no metadata file for Rockcraft)
        return models.BaseMetadata()


def _pack(
    *,
    prime_dir: pathlib.Path,
    project: Project,
    project_base_image: oci.Image,
    base_digest: bytes,
    rock_suffix: str,
    build_for: str,
    base_layer_dir: pathlib.Path,
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
    archive_name = f"{project.name}_{project.version}_{rock_suffix}.rock"
    new_image.to_oci_archive(tag=version, filename=archive_name)
    emit.progress(f"Exported to OCI archive '{archive_name}'")

    return archive_name
