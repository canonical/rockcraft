# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021 Canonical Ltd.
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

"""Buildd-related helpers for Rockcraft."""

from craft_providers import bases

BASE_TO_BUILDD_IMAGE_ALIAS = {
    "ubuntu:18.04": bases.BuilddBaseAlias.BIONIC,
    "ubuntu:20.04": bases.BuilddBaseAlias.FOCAL,
    "ubuntu:22.04": bases.BuilddBaseAlias.JAMMY,
}


class RockcraftBuilddBaseConfiguration(bases.BuilddBase):
    """Base configuration for Rockcraft.

    :cvar compatibility_tag: Tag/Version for variant of build configuration and
        setup.  Any change to this version would indicate that prior [versioned]
        instances are incompatible and must be cleaned.  As such, any new value
        should be unique to old values (e.g. incrementing).  Rockcraft extends
        the buildd tag to include its own version indicator (.0) and namespace
        ("rockcraft").
    """

    compatibility_tag: str = f"rockcraft-{bases.BuilddBase.compatibility_tag}.0"
