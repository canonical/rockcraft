# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2024 Canonical Ltd.
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

"""The Rockcraft Ant plugin."""
import logging

from craft_parts.plugins import ant_plugin
from overrides import override  # type: ignore[reportUnknownVariableType]

logger = logging.getLogger(__name__)


class AntPlugin(ant_plugin.AntPlugin):
    """An AntPlugin plugin for Rockcraft.

    This plugin extends Craft-parts' vanilla Ant plugin to properly
    use and install the Java VM. Specifically:

    - Do not link java executable to /bin/java
    """

    @override
    def _get_java_link_commands(self) -> list[str]:
        """Get the bash commands to provide /bin/java symlink."""
        return []
