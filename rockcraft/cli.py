# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021-2025 Canonical Ltd.
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

"""Command-line application entry point."""

from typing import Any

from craft_application import commands as appcommands
from craft_cli import CommandGroup, Dispatcher

from . import commands
from .application import Rockcraft
from .services import RockcraftServiceFactory, register_rockcraft_services

COMMAND_GROUPS: list[CommandGroup] = [
    CommandGroup(
        "Extensions",
        [
            commands.ExtensionsCommand,
            commands.ListExtensionsCommand,
            commands.ExpandExtensionsCommand,
        ],
    ),
    CommandGroup("Lifecycle", [appcommands.TestCommand, appcommands.RemoteBuild]),
]


def fill_command_groups(app: Rockcraft) -> None:
    """Fill in the command groups for an application instance."""
    for group in COMMAND_GROUPS:
        app.add_command_group(group.name, group.commands)


def run() -> int:
    """Command-line interface entrypoint."""
    app = _create_app()

    return app.run()


def _create_app() -> "Rockcraft":
    # pylint: disable=import-outside-toplevel
    # Import these here so that the script that generates the docs for the
    # commands doesn't need to know *too much* of the application.
    from .application import APP_METADATA, Rockcraft

    register_rockcraft_services()
    services = RockcraftServiceFactory(
        app=APP_METADATA,
    )

    app = Rockcraft(app=APP_METADATA, services=services)

    fill_command_groups(app)

    return app


def get_app_info() -> tuple[Dispatcher, dict[str, Any]]:
    """Retrieve application info. Used by craft-cli's completion module."""
    app = _create_app()
    dispatcher = app._create_dispatcher()  # type: ignore[reportPrivateUsage] # noqa: SLF001 (private member accessed)

    return dispatcher, app.app_config
