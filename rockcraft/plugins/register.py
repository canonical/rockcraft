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

from .jlink_plugin import JLinkPlugin
from .poetry_plugin import PoetryPlugin
from .python_plugin import PythonPlugin


def register() -> None:
    """Register Rockcraft plugins."""
    craft_parts.plugins.register(get_plugins())


def get_plugins() -> dict[str, PluginType]:
    """Get a dict of Rockcraft-specific plugins."""
    return {"jlink": JLinkPlugin, "poetry": PoetryPlugin, "python": PythonPlugin}
