# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2022 Canonical Ltd.
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


"""Rockcraft-specific code to interface with craft-providers."""

import os
import pathlib
from typing import Dict, Optional

from craft_providers import bases

BASE_TO_BUILDD_IMAGE_ALIAS = {
    "ubuntu:18.04": bases.BuilddBaseAlias.BIONIC,
    "ubuntu:20.04": bases.BuilddBaseAlias.FOCAL,
    "ubuntu:22.04": bases.BuilddBaseAlias.JAMMY,
}


def get_command_environment() -> Dict[str, Optional[str]]:
    """Construct the required environment."""
    env = bases.buildd.default_command_environment()
    env["ROCKCRAFT_MANAGED_MODE"] = "1"

    # Pass-through host environment that target may need.
    for env_key in ["http_proxy", "https_proxy", "no_proxy"]:
        if env_key in os.environ:
            env[env_key] = os.environ[env_key]

    return env


def get_instance_name(
    *,
    project_name: str,
    project_path: pathlib.Path,
) -> str:
    """Formulate the name for an instance using each of the given parameters.

    Incorporate each of the parameters into the name to come up with a
    predictable naming schema that avoids name collisions across multiple
    projects.

    :param project_name: Name of the project.
    :param project_path: Directory of the project.
    """
    return "-".join(
        [
            "rockcraft",
            project_name,
            str(project_path.stat().st_ino),
        ]
    )
