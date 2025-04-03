# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021 Canonical Ltd.
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

"""Utilities for rockcraft."""

import logging
import os
import pathlib
import shutil
from typing import NamedTuple

import rockcraft.errors

logger = logging.getLogger(__name__)


class OSPlatform(NamedTuple):
    """Tuple containing the OS platform information."""

    system: str
    release: str
    machine: str


def get_managed_environment_home_path() -> pathlib.Path:
    """Path for home when running in managed environment."""
    return pathlib.Path("/root")


def get_managed_environment_project_path() -> pathlib.Path:
    """Path for project when running in managed environment."""
    return get_managed_environment_home_path() / "project"


def get_managed_environment_log_path() -> pathlib.Path:
    """Path for log when running in managed environment."""
    return pathlib.Path("/tmp/rockcraft.log")  # noqa: S108


def get_managed_environment_snap_channel() -> str | None:
    """User-specified channel to use when installing Rockcraft snap from Snap Store.

    :returns: Channel string if specified, else None.
    """
    return os.getenv("ROCKCRAFT_INSTALL_SNAP_CHANNEL")


def _find_command_path_in_root(root: str, command_name: str) -> str | None:
    """Find the path of a command in a given root path."""
    for bin_directory in (
        "usr/local/sbin",
        "usr/local/bin",
        "usr/sbin",
        "usr/bin",
        "sbin",
        "bin",
    ):
        path = pathlib.Path(root) / bin_directory / command_name
        if path.exists():
            return str(path)

    return None


def get_host_command(command_name: str) -> str:
    """Return the full path of the given host tool.

    :param command_name: the name of the command to resolve a path for.
    :return: Path to command

    :raises RockcraftError: if command_name was not found.
    """
    tool = shutil.which(command_name)
    if not tool:
        raise rockcraft.errors.RockcraftError(
            f"A tool rockcraft depends on could not be found: {command_name!r}",
            resolution="Ensure the tool is installed and available, and try again.",
        )
    return tool


def get_snap_command_path(command_name: str) -> str:
    """Return the path of a command found in the snap.

    If rockcraft is not running as a snap, shutil.which() is used
    to resolve the command using PATH.

    :param command_name: the name of the command to resolve a path for.
    :return: Path to command

    :raises RockcraftError: if command_name was not found.
    """
    if os.environ.get("SNAP_NAME") != "rockcraft":
        return get_host_command(command_name)

    snap_path = os.getenv("SNAP")
    if snap_path is None:
        raise RuntimeError(
            "The SNAP environment variable is not defined, but SNAP_NAME is?"
        )

    command_path = _find_command_path_in_root(snap_path, command_name)

    if command_path is None:
        raise rockcraft.errors.RockcraftError(
            f"Cannot find snap tool {command_name!r}",
            resolution="Please report this error to the Rockcraft maintainers.",
        )

    return command_path
