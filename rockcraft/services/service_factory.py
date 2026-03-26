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

"""Rockcraft Service Factory."""

from typing import TYPE_CHECKING

from craft_application import ServiceFactory

# Add new services to this mapping to add them to the service factory
# Internal service name : Stringified service class name
_SERVICES: dict[str, str] = {
    "init": "RockcraftInitService",
    "lifecycle": "RockcraftLifecycleService",
    "package": "RockcraftPackageService",
    "provider": "RockcraftProviderService",
    "project": "RockcraftProjectService",
    "remote_build": "RockcraftRemoteBuildService",
    "image": "RockcraftImageService",
}


class RockcraftServiceFactory(ServiceFactory):
    """Rockcraft-specific Service Factory."""

    if TYPE_CHECKING:
        from rockcraft.services import RockcraftImageService

        image: RockcraftImageService = None  # type: ignore[assignment]


def register_rockcraft_services() -> None:
    """Register Rockcraft-specific services."""
    for name, service in _SERVICES.items():
        module_name = name.replace("_", "")
        RockcraftServiceFactory.register(
            name, service, module=f"rockcraft.services.{module_name}"
        )
