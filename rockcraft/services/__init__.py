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

"""Rockcraft services."""

from rockcraft.services.image import RockcraftImageService
from rockcraft.services.init import RockcraftInitService
from rockcraft.services.lifecycle import RockcraftLifecycleService
from rockcraft.services.package import RockcraftPackageService
from rockcraft.services.project import RockcraftProjectService
from rockcraft.services.provider import RockcraftProviderService
from rockcraft.services.remotebuild import RockcraftRemoteBuildService
from rockcraft.services.service_factory import (
    RockcraftServiceFactory,
    register_rockcraft_services,
)

__all__ = [
    "RockcraftImageService",
    "RockcraftInitService",
    "RockcraftLifecycleService",
    "RockcraftPackageService",
    "RockcraftProjectService",
    "RockcraftProviderService",
    "RockcraftServiceFactory",
    "RockcraftRemoteBuildService",
    "register_rockcraft_services",
]
