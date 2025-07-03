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


import argparse
import datetime
import json
from collections.abc import Iterable
from importlib import resources
from typing import TYPE_CHECKING, Any, cast

from craft_application.commands import ExtensibleCommand
from craft_cli import CraftError, emit

if TYPE_CHECKING:
    from rockcraft.models.project import Project


def is_eol(base: str) -> bool:
    """Check if the given base is EOL."""
    eol_data_file = resources.files("rockcraft").joinpath("data/ubuntu.json")
    with eol_data_file.open("r") as f:
        eol_data = json.load(f)
    if base not in eol_data:
        raise ValueError(f"Unknown Ubuntu version {base}")
    version_data = eol_data[base]
    return datetime.date.today() >= datetime.date.fromisoformat(version_data["eol-esm"])


def _parse_unsupported_base(
    cmd: ExtensibleCommand, parser: argparse.ArgumentParser
) -> None:
    """Extend the parser to include accepting an unsupported base."""
    parser.add_argument(
        "--ack-unsupported-base",
        action="store_true",
        dest="allow_unsupported_base",
        help="Allow building for an unsupported base",
    )
    # TODO: Remove this until we actually have Ubuntu pro support.
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use Ubuntu Pro (ONLY FOR DEMO PURPOSES DOESN'T REALLY DO ANYTHING)",
    )


def _check_unsupported_base(
    cmd: ExtensibleCommand, parsed_args: argparse.Namespace, **kwargs: Any
) -> int | None:
    if parsed_args.allow_unsupported_base:
        return  # Don't care what the base is if we're allowing unsupported bases!
    project = cast("Project", cmd._services.get("project").get())
    distro, _, version = project.base.partition("@")

    if distro != "ubuntu":
        # TODO: Eventually we might need logic here?
        return

    eol_data_file = resources.files("rockcraft").joinpath("data/ubuntu.json")
    with eol_data_file.open("r") as f:
        eol_data = json.load(f)
    if version not in eol_data:
        raise ValueError(f"Unknown Ubuntu version {version}")
    version_data = eol_data[version]
    today = datetime.date.today()
    if today < datetime.date.fromisoformat(version_data["release"]):
        # Pre-release, must have build-base devel
        if project.build_base != "devel":
            raise CraftError("Pre-release bases must include 'build-base: devel'")
    elif today < datetime.date.fromisoformat(version_data["eol"]):
        emit.trace("Base is currently supported.")
    elif today < datetime.date.fromisoformat(version_data["eol-esm"]):
        if parsed_args.pro:  # TODO: Pro not supported yet.
            emit.debug("EOL, ESM-supported base while using Pro.")
        elif parsed_args.allow_unsupported_base:
            emit.progress(
                f"WARNING: {project.base} is end-of-life and only supported with Ubuntu Pro."
            )
        else:
            raise CraftError(
                f"Base is end of life: {project.base}",
                resolution=f"Use --pro to get support until {version_data['eol-esm']}.",
            )
    elif parsed_args.allow_unsupported_base:
        emit.progress(f"WARNING: {project.base} is end-of-life.")
    else:
        raise CraftError(
            f"Base is end of life: {project.base}",
            resolution="Switch to a newer base or use --ack-unsupported-base to accept building on an unsupported base with potential security vulnerabilities.",
        )


def extend_unsupported_bases(commands: Iterable[type[ExtensibleCommand]]) -> None:
    """Extend the given commands to include an `--ack-unsupported-base` parameter."""
    for command in commands:
        command.register_parser_filler(_parse_unsupported_base)
        command.register_prologue(_check_unsupported_base)
