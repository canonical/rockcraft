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
from typing import Optional

from craft_parts.plugins import python_plugin
from overrides import override

logger = logging.getLogger(__name__)


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
        return "#!/bin/python3"
