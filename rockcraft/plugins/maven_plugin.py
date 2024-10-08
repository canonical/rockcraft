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

"""The Rockcraft Maven plugin."""
import logging
from textwrap import dedent

from craft_parts.plugins import maven_plugin
from overrides import override  # type: ignore[reportUnknownVariableType]

logger = logging.getLogger(__name__)

# Template for the sitecustomize module that we'll add to the payload so that
# the pip-installed packages are found regardless of how the interpreter is
# called.
SITECUSTOMIZE_TEMPLATE = dedent(
    """
    # sitecustomize added by Rockcraft.
    import site
    import sys

    major, minor = sys.version_info.major, sys.version_info.minor
    site_dir = f"/lib/python{major}.{minor}/site-packages"
    dist_dir = "/usr/lib/python3/dist-packages"

    # Add the directory that contains the venv-installed packages.
    site.addsitedir(site_dir)

    if dist_dir in sys.path:
        # Make sure that this site-packages dir comes *before* the base-provided
        # dist-packages dir in sys.path.
        path = sys.path
        site_index = path.index(site_dir)
        dist_index = path.index(dist_dir)

        if dist_index < site_index:
            path[dist_index], path[site_index] = path[site_index], path[dist_index]

    EOF
    """
).strip()


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
        env["PATH"] = "/usr/bin"
        return env
