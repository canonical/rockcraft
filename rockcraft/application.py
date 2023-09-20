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

"""Main Rockcraft Application."""

from __future__ import annotations

import functools
import os
import pathlib
import signal
import sys

import craft_cli
from craft_application import Application, AppMetadata, util
from craft_application.application import _Dispatcher
from craft_application.commands import get_lifecycle_command_group
from craft_cli import CommandGroup
from overrides import override

from rockcraft import models
from rockcraft.models import project

APP_METADATA = AppMetadata(
    name="rockcraft",
    summary="A tool to create OCI images",
    ProjectClass=project.Project,
    source_ignore_patterns=["*.rock"],
)


class FallbackRunError(RuntimeError):
    """Run should be handled by the legacy code."""


class Rockcraft(Application):
    """Rockcraft application definition."""

    @property
    @override
    def command_groups(self) -> list[craft_cli.CommandGroup]:
        """Filter supported command from CraftApplication."""
        all_lifecycle_commands = get_lifecycle_command_group().commands
        migrated_commands = {"pack"}

        return [
            CommandGroup(
                "Lifecycle",
                [c for c in all_lifecycle_commands if c.name in migrated_commands],
            )
        ]

    @functools.cached_property
    def project(self) -> models.Project:
        """Get this application's Project metadata."""
        project_file = (pathlib.Path.cwd() / f"{self.app.name}.yaml").resolve()
        craft_cli.emit.debug(f"Loading project file '{project_file!s}'")
        return models.Project.from_yaml_file(project_file, work_dir=self._work_dir)

    @override
    def _get_dispatcher(self) -> _Dispatcher:
        """Overridden to raise a FallbackRunError() for unhandled commands.

        Should be removed after we finish migrating all commands.
        """
        craft_cli.emit.init(
            mode=craft_cli.EmitterMode.BRIEF,
            appname=self.app.name,
            greeting=f"Starting {self.app.name}",
            log_filepath=self.log_path,
            streaming_brief=True,
        )

        dispatcher = _Dispatcher(
            self.app.name,
            self.command_groups,
            summary=str(self.app.summary),
            extra_global_args=self._global_arguments,
        )

        try:
            craft_cli.emit.trace("pre-parsing arguments...")
            # Workaround for the fact that craft_cli requires a command.
            # https://github.com/canonical/craft-cli/issues/141
            if "--version" in sys.argv or "-V" in sys.argv:
                try:
                    global_args = dispatcher.pre_parse_args(["pull", *sys.argv[1:]])
                except craft_cli.ArgumentParsingError:
                    global_args = dispatcher.pre_parse_args(sys.argv[1:])
            else:
                global_args = dispatcher.pre_parse_args(sys.argv[1:])

            if global_args.get("version"):
                craft_cli.emit.ended_ok()
                print(f"{self.app.name} {self.app.version}")
                sys.exit(0)
            # Try loading the command to shake out possible ArgumentParsingErrors
            # from commands with options that we can't handle yet (like
            # --destructive-mode)
            dispatcher.load_command(
                {
                    "app": self.app,
                    "services": self.services,
                }
            )
        except (craft_cli.ProvideHelpException, craft_cli.ArgumentParsingError) as err:
            # Difference from base's behavior: fallback to the legacy run
            # if we get an unknown command, or an invalid option, or a request
            # for help.
            raise FallbackRunError() from err
        except KeyboardInterrupt as err:
            self._emit_error(craft_cli.CraftError("Interrupted."), cause=err)
            sys.exit(128 + signal.SIGINT)
        except Exception as err:  # pylint: disable=broad-except
            self._emit_error(
                craft_cli.CraftError(
                    f"Internal error while loading {self.app.name}: {err!r}"
                )
            )
            if os.getenv("CRAFT_DEBUG") == "1":
                raise
            sys.exit(70)  # EX_SOFTWARE from sysexits.h

        craft_cli.emit.trace("Preparing application...")
        self.configure(global_args)

        return dispatcher

    def _configure_services(self, build_for: str | None) -> None:
        if build_for is None:
            build_for = util.get_host_architecture()

        self.services.set_kwargs("image", work_dir=self._work_dir, build_for=build_for)
        self.services.set_kwargs(
            "package",
            build_for=build_for,
        )
        super()._configure_services(build_for)
