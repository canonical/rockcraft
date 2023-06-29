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

"""The Rockcraft Python plugin."""

import logging
from textwrap import dedent
from typing import List, Optional

from craft_parts.plugins import python_plugin
from overrides import override

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


class PythonPlugin(python_plugin.PythonPlugin):
    """A Python plugin for Rockcraft.

    This plugin extends Craft-parts' vanilla Python plugin to properly
    set the Python interpreter according to the ROCK's base. Specifically:

    - If the base is ubuntu, the venv-created symlinks in bin/ are removed
      altogether. This is because of the usrmerge; when the layer is added on
      top of the base ubuntu layer bin/ becomes a symlink to usr/bin/, so there
      already is a usable Python binary in bin/.
    - Since no base (bare or any ubuntu) provides Python by default, the base
      interpreter must always be provided by one of the parts. The easiest way
      to accomplish this is to add "python3-venv" as a stage-package.
    - The shebang in console scripts is hardcoded to "#!/bin/python3". In fact,
      every use of Python in the resulting image should be via /bin/python3.
    """

    @override
    def _should_remove_symlinks(self) -> bool:
        """Overridden because for ubuntu bases we must always remove the symlinks."""
        return self._part_info.base != "bare"

    @override
    def _get_system_python_interpreter(self) -> Optional[str]:
        """Overridden because Python must always be provided by the parts."""
        return None

    @override
    def _get_script_interpreter(self) -> str:
        """Overridden because Python is always available in /bin/python3."""
        return "#!/bin/${PARTS_PYTHON_INTERPRETER}"

    @override
    def get_build_commands(self) -> List[str]:
        """Overridden to add a sitecustomize.py ."""
        original = super().get_build_commands()

        # Add a "sitecustomize.py" module to handle the very common case of the
        # ROCK's interpreter being called as "python3"; in this case, because of
        # the default $PATH, "/usr/bin/python3" ends up being called and that is
        # *not* the venv-aware executable. This sitecustomize adds the location
        # of the pip-installed packages.
        original.append(
            dedent(
                """
                # Add a sitecustomize.py to import our venv-generated location
                py_version=$(basename $payload_python)
                py_dir=${CRAFT_PART_INSTALL}/usr/lib/${py_version}/
                mkdir -p ${py_dir}
                cat << EOF > ${py_dir}/sitecustomize.py
                """
            )
        )
        original.append(SITECUSTOMIZE_TEMPLATE)

        # Remove the pyvenv.cfg file that "marks" the virtual environment, because
        # it's not necessary in the presence of the sitecustomize module and this
        # way we get consistent behavior no matter how the interpreter is called.
        original.append(
            dedent(
                """
                # Remove pyvenv.cfg file in favor of sitecustomize.py
                rm ${CRAFT_PART_INSTALL}/pyvenv.cfg
                """
            )
        )

        return original
