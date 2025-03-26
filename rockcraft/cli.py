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

from typing import TYPE_CHECKING, Any

from craft_application import commands as appcommands
from craft_cli import Dispatcher

from . import commands
from .services import RockcraftServiceFactory

if TYPE_CHECKING:
    from .application import Rockcraft


def run() -> int:
    """Command-line interface entrypoint."""
    app = _create_app()

    return app.run()


def _create_app() -> "Rockcraft":
    # pylint: disable=import-outside-toplevel
    # Import these here so that the script that generates the docs for the
    # commands doesn't need to know *too much* of the application.
    from .application import APP_METADATA, Rockcraft

    services = RockcraftServiceFactory(
        app=APP_METADATA,
    )

    app = Rockcraft(app=APP_METADATA, services=services)

    app.add_command_group(
        "Extensions",
        [
            commands.ExtensionsCommand,
            commands.ListExtensionsCommand,
            commands.ExpandExtensionsCommand,
        ],
    )

    app.add_command_group("Lifecycle", [appcommands.RemoteBuild])

    return app


def get_app_info() -> tuple[Dispatcher, dict[str, Any]]:
    """Retrieve application info. Used by craft-cli's completion module."""
    app = _create_app()
    dispatcher = app._create_dispatcher()  # type: ignore[reportPrivateUsage] # noqa: SLF001 (private member accessed)

    return dispatcher, app.app_config
