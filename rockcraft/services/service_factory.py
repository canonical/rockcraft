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

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from craft_application import ServiceFactory
from craft_application import services as base_services

from rockcraft import services


@dataclass
class RockcraftServiceFactory(ServiceFactory):
    """Rockcraft-specific Service Factory."""

    # pylint: disable=invalid-name

    ImageClass: type[services.RockcraftImageService] = services.RockcraftImageService
    PackageClass: type[base_services.PackageService] = services.RockcraftPackageService
    ProviderClass: type[
        services.RockcraftProviderService
    ] = services.RockcraftProviderService

    if TYPE_CHECKING:
        image: services.RockcraftImageService = None  # type: ignore[assignment]
