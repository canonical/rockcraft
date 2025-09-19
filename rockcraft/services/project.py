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
from pathlib import Path
from typing import Any

import craft_platforms
from craft_application import ProjectService
from typing_extensions import override

from rockcraft.extensions._utils import apply_extensions
from rockcraft.pebble import add_pebble_part


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

    @staticmethod
    @override
    def _is_supported_on(
        *, base: craft_platforms.DistroBase, date: datetime.date
    ) -> bool:
        """Temporary override for 'devel' bases."""
        if base.series == "devel":
            return True
        return ProjectService._is_supported_on(base=base, date=date)  # noqa: SLF001 (private member access)
