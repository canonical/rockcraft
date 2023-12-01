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

import logging

from rockcraft import plugins

from . import commands
from .services import RockcraftServiceFactory


def run() -> int:
    """Command-line interface entrypoint."""
    # Register our own plugins
    plugins.register()

    # set lib loggers to debug level so that all messages are sent to Emitter
    for lib_name in ("craft_providers", "craft_parts"):
        logger = logging.getLogger(lib_name)
        logger.setLevel(logging.DEBUG)

    app = _create_app()

    return app.run()  # type: ignore[no-any-return]


def _create_app():  # type: ignore[no-untyped-def] # noqa: ANN202
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
        "Other",
        [
            commands.InitCommand,
        ],
    )
    app.add_command_group(
        "Extensions",
        [
            commands.ExtensionsCommand,
            commands.ListExtensionsCommand,
            commands.ExpandExtensionsCommand,
        ],
    )

    return app
