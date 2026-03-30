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

"""Rockcraft Project service."""

import datetime
import textwrap
from pathlib import Path
from typing import Any

import craft_platforms
from craft_application import ProjectService
from craft_application.errors import CraftValidationError
from typing_extensions import override

from rockcraft.extensions._utils import apply_extensions
from rockcraft.pebble import add_pebble_part

# Part to execute apt-get upgrade in an overlay.
# Currently only enabled if the project is built with pro sources.
APT_UPGRADE_PART = {
    "plugin": "nil",
    "override-overlay": textwrap.dedent("""
        # At the moment, we only upgrade the base system packages in the overlay
        # if we are building with pro sources.
        if find /etc/apt/sources.list.d/ -iname "ubuntu-esm-*.sources" -or -iname "ubuntu-fips-*.sources"; then
            echo "Upgrading base overlay system packages"
            apt-get update
            apt-get -y upgrade
            apt-get clean
            rm -rf /var/cache/apt
        else
            echo "Ubuntu Pro sources not found; skipping base overlay upgrade
        fi
    """).strip(),
}


class RockcraftProjectService(ProjectService):
    """Rockcraft-specific project service."""

    @staticmethod
    @override
    def _app_preprocess_project(
        project: dict[str, Any], *, build_on: str, build_for: str, platform: str
    ) -> None:
        """Apply preprocessing for Rockcraft projects."""
        project_root = Path.cwd()
        apply_extensions(project_root=project_root, yaml_data=project)
        add_pebble_part(project)
        _add_apt_upgrade_data(project)

    @staticmethod
    @override
    def _is_supported_on(
        *, base: craft_platforms.DistroBase, date: datetime.date
    ) -> bool:
        """Temporary override for 'devel' bases."""
        if base.series == "devel":
            return True
        return ProjectService._is_supported_on(base=base, date=date)  # noqa: SLF001 (private member access)


def _add_apt_upgrade_data(yaml_data: dict[str, Any]) -> None:
    """Add hidden part to execute apt-get upgrade in an overlay."""
    part_name = "_apt-upgrade"

    if yaml_data.get("base", "unknown") == "bare":
        # Skip adding the part to bare projects as executing apt-get upgrade
        # would not make sense without a Ubuntu base.
        return

    if "parts" not in yaml_data:
        # Invalid project: let it return to fail in the regular validation flow.
        return

    parts = yaml_data["parts"]
    if (existing := parts.get(part_name)) is not None and existing != APT_UPGRADE_PART:
        raise CraftValidationError(f'Cannot override the default "{part_name}" part.')

    parts[part_name] = APT_UPGRADE_PART
