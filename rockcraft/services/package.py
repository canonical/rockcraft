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

from __future__ import annotations

import datetime
import pathlib
import typing
from typing import cast

from craft_application import AppMetadata, PackageService, models, util
from craft_cli import emit
from overrides import override

from rockcraft import errors, oci
from rockcraft.models import Project
from rockcraft.usernames import SUPPORTED_GLOBAL_USERNAMES

if typing.TYPE_CHECKING:
    from rockcraft.services import RockcraftServiceFactory


class RockcraftPackageService(PackageService):
    """Package service subclass for Rockcraft."""

    def __init__(
        self,
        app: AppMetadata,
        services: RockcraftServiceFactory,
        *,
        project: models.Project,
        platform: str | None,
        build_for: str,
    ) -> None:
        super().__init__(app, services, project=project)
        self._platform = platform
        self._build_for = build_for

    @override
    def pack(self, prime_dir: pathlib.Path, dest: pathlib.Path) -> list[pathlib.Path]:
        """Create one or more packages as appropriate.

        :param dest: Directory into which to write the package(s).
        :returns: A list of paths to created packages.
        """
        # This inner import is necessary to resolve a cyclic import
        # pylint: disable=import-outside-toplevel
        from rockcraft.services import RockcraftServiceFactory

        services = cast(RockcraftServiceFactory, self._services)
        image_service = services.image
        image_info = image_service.obtain_image()

        platform = self._platform

        if platform is None:
            # This should only happen in destructive mode, in which case we
            # can only pack a single ROCK.
            build_on = util.get_host_architecture()
            base_build_plan = self._project.get_build_plan()
            build_plan = [
                plan for plan in base_build_plan if plan.build_for == self._build_for
            ]
            build_plan = [plan for plan in build_plan if plan.build_on == build_on]

            if len(build_plan) != 1:
                message = "Unable to determine which platform to build."
                details = f"Possible values are: {[info.platform for info in base_build_plan]}."
                resolution = 'Choose a platform with the "--platform" parameter.'
                raise errors.RockcraftError(
                    message=message, details=details, resolution=resolution
                )

            platform = build_plan[0].platform

        archive_name = _pack(
            prime_dir=prime_dir,
            project=cast(Project, self._project),
            project_base_image=image_info.base_image,
            base_digest=image_info.base_digest,
            rock_suffix=platform,
            build_for=self._build_for,
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

    new_image.set_entrypoint(project.entrypoint_service)
    if project.services and project.entrypoint_service in project.services:
        new_image.set_cmd(project.services[project.entrypoint_service].command)

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
    emit.progress(f"Exported to OCI archive '{archive_name}'")

    return archive_name
