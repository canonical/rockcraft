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

import pathlib
import typing
from typing import cast

from craft_application import AppMetadata, PackageService, models, util
from overrides import override

from rockcraft.models import Project, RockcraftBuildInfo

if typing.TYPE_CHECKING:
    from rockcraft.services import RockcraftServiceFactory


class RockcraftPackageService(PackageService):
    """Package service subclass for Rockcraft."""

    def __init__(
        self,
        app: AppMetadata,
        project: models.Project,
        services: RockcraftServiceFactory,
        *,
        build_for: str,
    ) -> None:
        super().__init__(app, project, services)
        self._build_for = build_for

    @override
    def pack(self, prime_dir: pathlib.Path, dest: pathlib.Path) -> list[pathlib.Path]:
        """Create one or more packages as appropriate.

        :param dest: Directory into which to write the package(s).
        :returns: A list of paths to created packages.
        """
        # pylint: disable=import-outside-toplevel
        # This import stays here until we refactor 'lifecycle' completely out.
        from rockcraft.lifecycle import _pack

        # This inner import is necessary to resolve a cyclic import
        from rockcraft.services import RockcraftServiceFactory

        services = cast(RockcraftServiceFactory, self._services)
        image_service = services.image
        image_info = image_service.obtain_image()

        build_on = util.get_host_architecture()
        build_plan = self._project.get_build_plan()
        build_plan = [plan for plan in build_plan if plan.build_for == self._build_for]
        build_plan = [plan for plan in build_plan if plan.build_on == build_on]

        if len(build_plan) != 1:
            raise RuntimeError(f"Don't know which build to pack: {build_plan}")

        build_info = cast(RockcraftBuildInfo, build_plan[0])

        archive_name = _pack(
            prime_dir=prime_dir,
            project=cast(Project, self._project),
            project_base_image=image_info.base_image,
            base_digest=image_info.base_digest,
            rock_suffix=build_info.platform_entry,
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
