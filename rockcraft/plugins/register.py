# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2022 Canonical Ltd.
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

"""Rockcraft-provided plugin registration."""

import craft_parts
from craft_parts.plugins.plugins import PluginType

from .ant_plugin import AntPlugin
from .maven_plugin import MavenPlugin
from .python_common import get_python_plugins


def register(base: str | None) -> None:
    """Register Rockcraft plugins for a given base."""
    craft_parts.plugins.register(get_plugins(base))


def get_plugins(base: str | None) -> dict[str, PluginType]:
    """Get a dict of Rockcraft-specific plugins for a given base."""
    return {
        "ant": AntPlugin,
        "maven": MavenPlugin,
    } | get_python_plugins(base)
