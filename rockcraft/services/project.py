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

from pathlib import Path
from typing import Any

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
