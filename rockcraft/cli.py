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

import craft_cli
from craft_cli import ArgumentParsingError, EmitterMode, ProvideHelpException, emit

from rockcraft import __version__

from . import commands

COMMAND_GROUPS = [
    craft_cli.CommandGroup(
        "Lifecycle",
        [
            commands.PullCommand,
            commands.OverlayCommand,
            commands.BuildCommand,
            commands.StageCommand,
            commands.PrimeCommand,
            commands.PackCommand,
        ],
    )
]

GLOBAL_ARGS = [
    craft_cli.GlobalArgument(
        "version", "flag", "-V", "--version", "Show the application version and exit"
    )
]


def run():
    """Run the CLI."""
    # set lib loggers to debug level so that all messages are sent to Emitter
    for lib_name in ("craft_providers", "craft_parts"):
        logger = logging.getLogger(lib_name)
        logger.setLevel(logging.DEBUG)

    emit_args = {
        "mode": EmitterMode.NORMAL,
        "appname": "rockcraft",
        "greeting": f"Starting Rockcraft {__version__}",
    }

    emit.init(**emit_args)

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
    except craft_cli.CraftError as err:  # TODO: define RockcraftError
        emit.error(err)
        sys.exit(1)
