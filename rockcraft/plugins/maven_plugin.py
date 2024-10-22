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

"""The Rockcraft Maven plugin."""
import logging

from craft_parts.plugins import maven_plugin
from overrides import override  # type: ignore[reportUnknownVariableType]

logger = logging.getLogger(__name__)

class MavenPlugin(maven_plugin.MavenPlugin):
    """A MavenPlugin plugin for Rockcraft.

    This plugin extends Craft-parts' vanilla Maven plugin to properly
    use and install the Java VM. Specifically:

    - Do not link java executable to /bin/java
    - Do not include staging area in the PATH
    """

    @override
    def _get_java_link_commands(self) -> list[str]:
        """Get the bash commands to provide /bin/java symlink."""
        return []

    @override
    def get_build_environment(self) -> dict[str, str]:
        env = super().get_build_environment()
        env["PATH"] = "/usr/bin:$PATH"
        return env
