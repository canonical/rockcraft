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
import sys
from typing import Optional

import craft_cli
from craft_cli import ArgumentParsingError, ProvideHelpException, emit
from craft_parts import PartsError
from craft_providers import ProviderError

from rockcraft import __version__, errors, plugins

from . import commands
from .services import RockcraftServiceFactory
from .utils import is_managed_mode

COMMAND_GROUPS = [
    craft_cli.CommandGroup(
        "Lifecycle",
        [
            commands.CleanCommand,
            commands.PullCommand,
            commands.OverlayCommand,
            commands.BuildCommand,
            commands.StageCommand,
            commands.PrimeCommand,
            commands.PackCommand,
        ],
    ),
    craft_cli.CommandGroup(
        "Extensions",
        [
            commands.ExtensionsCommand,
            commands.ListExtensionsCommand,
            commands.ExpandExtensionsCommand,
        ],
    ),
    craft_cli.CommandGroup(
        "Other",
        [
            commands.InitCommand,
        ],
    ),
]

GLOBAL_ARGS = [
    craft_cli.GlobalArgument(
        "version", "flag", "-V", "--version", "Show the application version and exit"
    )
]


def run() -> None:
    """Command-line interface entrypoint."""
    # pylint: disable=import-outside-toplevel
    # Import these here so that the script that generates the docs for the
    # commands doesn't need to know *too much* of the application.
    from .application import APP_METADATA, FallbackRunError, Rockcraft

    # Register our own plugins
    plugins.register()

    # set lib loggers to debug level so that all messages are sent to Emitter
    for lib_name in ("craft_providers", "craft_parts"):
        logger = logging.getLogger(lib_name)
        logger.setLevel(logging.DEBUG)

    services = RockcraftServiceFactory(
        # type: ignore # type: ignore[call-arg]
        app=APP_METADATA,
    )

    app = Rockcraft(app=APP_METADATA, services=services)

    try:
        app.run()
    except FallbackRunError:
        legacy_run()


def _emit_error(error: craft_cli.CraftError, cause: Optional[Exception] = None) -> None:
    """Emit the error in a centralized way so we can alter it consistently."""
    # set the cause, if any
    if cause is not None:
        error.__cause__ = cause

    # if running inside a managed instance, do not report the internal logpath
    if is_managed_mode():
        error.logpath_report = False

    # finally, emit
    emit.error(error)


def legacy_run() -> None:
    """Run the CLI."""
    dispatcher = craft_cli.Dispatcher(
        "rockcraft",
        COMMAND_GROUPS,
        summary="A tool to create OCI images",
        extra_global_args=GLOBAL_ARGS,
        default_command=commands.PackCommand,
    )

    try:
        global_args = dispatcher.pre_parse_args(sys.argv[1:])
        if global_args.get("version"):
            emit.message(f"rockcraft {__version__}")
        else:
            dispatcher.load_command(None)
            dispatcher.run()
        emit.ended_ok()
    except ProvideHelpException as err:
        print(err, file=sys.stderr)  # to stderr, as argparse normally does
        emit.ended_ok()
    except ArgumentParsingError as err:
        print(err, file=sys.stderr)  # to stderr, as argparse normally does
        emit.ended_ok()
        sys.exit(1)
    except errors.RockcraftError as err:
        _emit_error(err)
        sys.exit(1)
    except PartsError as err:
        _emit_error(
            craft_cli.CraftError(
                err.brief, details=err.details, resolution=err.resolution
            )
        )
        sys.exit(1)
    except ProviderError as err:
        _emit_error(craft_cli.CraftError(f"craft-providers error: {err}"))
        sys.exit(1)
    except Exception as err:  # pylint: disable=broad-except
        _emit_error(craft_cli.CraftError(f"rockcraft internal error: {err!r}"))
        sys.exit(1)
