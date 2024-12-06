# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021-2022 Canonical Ltd.
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

from typing import TYPE_CHECKING

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
        # type: ignore # type: ignore[call-arg]
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
    app.add_command_group("Lifecycle", [commands.RemoteBuild])

    return app
