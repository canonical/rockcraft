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

"""Rockcraft Lifecycle service."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import cast

from craft_application import LifecycleService
from craft_archives import repo
from craft_cli import emit
from craft_parts import callbacks
from craft_parts.errors import CallbackRegistrationError
from overrides import override

from rockcraft.models.project import Project


class RockcraftLifecycleService(LifecycleService):
    """Rockcraft-specific lifecycle service."""

    @override
    def setup(self) -> None:
        """Initialize the LifecycleManager with previously-set arguments."""
        # pylint: disable=import-outside-toplevel
        # This inner import is necessary to resolve a cyclic import
        from rockcraft.services import RockcraftServiceFactory

        # Configure extra args to the LifecycleManager
        project = cast(Project, self._project)
        project_vars = {"version": project.version}

        services = cast(RockcraftServiceFactory, self._services)
        image_service = services.image
        image_info = image_service.obtain_image()

        self._manager_kwargs.update(
            base_layer_dir=image_info.base_layer_dir,
            base_layer_hash=image_info.base_digest,
            base=project.base,
            package_repositories=project.package_repositories or [],
            project_name=project.name,
            project_vars=project_vars,
        )

        super().setup()

    @override
    def run(self, step_name: str | None, part_names: list[str] | None = None) -> None:
        """Run the lifecycle manager for the parts."""
        # Overridden to configure package repositories.
        project = cast(Project, self._project)
        package_repositories = project.package_repositories

        if package_repositories is not None:
            _install_package_repositories(package_repositories, self._lcm)
            with contextlib.suppress(CallbackRegistrationError):
                callbacks.register_configure_overlay(_install_overlay_repositories)

        super().run(step_name, part_names)


def _install_package_repositories(package_repositories, lifecycle_manager) -> None:
    """Install package repositories in the environment."""
    if not package_repositories:
        emit.debug("No package repositories specified, none to install.")
        return

    refresh_required = repo.install(package_repositories, key_assets=Path("/dev/null"))
    if refresh_required:
        emit.progress("Refreshing repositories")
        lifecycle_manager.refresh_packages_list()

    emit.progress("Package repositories installed", permanent=True)


def _install_overlay_repositories(overlay_dir, project_info):
    if project_info.base != "bare":
        package_repositories = project_info.package_repositories
        repo.install_in_root(
            project_repositories=package_repositories,
            root=overlay_dir,
            key_assets=Path("/dev/null"),
        )
