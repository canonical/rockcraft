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
from craft_application.errors import CraftValidationError
from typing_extensions import override

from rockcraft.extensions._utils import apply_extensions
from rockcraft.pebble import Pebble


class Project(ProjectService):
    """Rockcraft-specific project service."""

    @staticmethod
    @override
    def _app_preprocess_project(
        project: dict[str, Any], *, build_on: str, build_for: str, platform: str
    ) -> None:
        """Apply preprocessing for Rockcraft projects."""
        project_root = Path.cwd()
        apply_extensions(project_root=project_root, yaml_data=project)
        _add_pebble_data(project)


def _add_pebble_data(project: dict[str, Any]) -> None:
    """Add pebble-specific contents to YAML-loaded data.

    This function adds a special "pebble" part to a project's specification, to be
    (eventually) used as the image's entrypoint.

    :param project: The project spec loaded from "rockcraft.yaml" by the project
      service.
    :raises CraftValidationError: If `project` already contains a "pebble" part,
      and said part's contents are different from the contents of the part we add.
    """
    build_base = project["build-base"]
    pebble_part = Pebble.get_part_spec(build_base)

    parts = project["parts"]
    if "pebble" in parts:
        if parts["pebble"] == pebble_part:
            # Project already has the correct pebble part.
            return
        # Project already has a pebble part, and it's different from ours;
        # this is currently not supported.
        raise CraftValidationError('Cannot change the default "pebble" part')

    parts["pebble"] = pebble_part
