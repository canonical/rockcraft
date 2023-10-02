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

"""Utilities to expand variables in project environments."""

from __future__ import annotations

import pathlib
from typing import Any

import craft_parts


def expand_environment(
    project_yaml: dict[str, Any],
    *,
    project_vars: dict[str, Any],
    work_dir: pathlib.Path,
) -> None:
    """Expand global variables in the provided dictionary values.

    :param project_yaml: A dictionary containing the rockcraft.yaml's contents.
    :param project_var: A dictionary with the project-specific variables.
    :param work_dir: The working directory.
    """
    info = craft_parts.ProjectInfo(
        application_name="rockcraft",  # not used in environment expansion
        cache_dir=pathlib.Path(),  # not used in environment expansion
        project_name=project_yaml.get("name", ""),
        project_dirs=craft_parts.ProjectDirs(work_dir=work_dir),
        project_vars=project_vars,
    )
    _set_global_environment(info)

    craft_parts.expand_environment(project_yaml, info=info)


def _set_global_environment(info: craft_parts.ProjectInfo) -> None:
    """Set global environment variables."""
    info.global_environment.update(
        {
            "CRAFT_PROJECT_VERSION": info.get_project_var("version", raw_read=True),
        }
    )
