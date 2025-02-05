# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2025 Canonical Ltd.
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

"""The Rockcraft uv plugin."""

from textwrap import dedent

from craft_parts.plugins import uv_plugin
from overrides import override  # type: ignore[reportUnknownVariableType]

from rockcraft.plugins import python_common


class UvPlugin(uv_plugin.UvPlugin):
    """A uv plugin for Rockcraft."""

    @override
    def _should_remove_symlinks(self) -> bool:
        """Overridden because for ubuntu bases we must always remove the symlinks."""
        return python_common.should_remove_symlinks(self._part_info)

    @override
    def _get_system_python_interpreter(self) -> str | None:
        """Overridden because Python must always be provided by the parts.

        The uv plugin requires a name to reference Python, so we must depend
        on a relative python3 being installed. Should return None once
        https://github.com/canonical/craft-parts/issues/991 is closed."""
        return "python3"

    @override
    def _get_script_interpreter(self) -> str:
        """Overridden because Python is always available in /bin."""
        return python_common.get_script_interpreter()

    @override
    def _get_rewrite_shebangs_commands(self) -> list[str]:
        """Overridden because the original uv plugin does not rewrite shebangs."""
        script_interpreter = self._get_script_interpreter()
        find_cmd = (
            f'find "{self._part_info.part_install_dir}" -type f -executable -print0'
        )
        xargs_cmd = "xargs --no-run-if-empty -0"
        sed_cmd = f'sed -i "1 s|^#\\!.*$|{script_interpreter}|"'
        return [
            dedent(
                f"""\
                {find_cmd} | {xargs_cmd} \\
                    {sed_cmd}
                """
            )
        ]

    @override
    def get_build_commands(self) -> list[str]:
        """Overridden to add a sitecustomize.py."""
        return python_common.wrap_build_commands(super().get_build_commands())
