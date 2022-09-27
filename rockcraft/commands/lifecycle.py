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

"""Rockcraft lifecycle commands."""

import abc
import textwrap
from typing import TYPE_CHECKING

from craft_cli import BaseCommand, emit
from overrides import overrides

from rockcraft import lifecycle

if TYPE_CHECKING:
    import argparse


class _LifecycleCommand(BaseCommand, abc.ABC):
    """Lifecycle-related commands."""

    @overrides
    def run(self, parsed_args):
        """Run the command."""
        if not self.name:
            raise RuntimeError("command name not specified")

        emit.trace(f"lifecycle command: {self.name!r}, arguments: {parsed_args!r}")
        lifecycle.run(self.name, parsed_args)


class _LifecycleStepCommand(_LifecycleCommand):
    """Lifecycle step commands."""

    @overrides
    def fill_parser(self, parser: "argparse.ArgumentParser") -> None:
        super().fill_parser(parser)  # type: ignore
        parser.add_argument(
            "parts",
            metavar="part-name",
            type=str,
            nargs="*",
            help="Optional list of parts to process",
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--shell",
            action="store_true",
            help="Shell into the environment in lieu of the step to run.",
        )
        group.add_argument(
            "--shell-after",
            action="store_true",
            help="Shell into the environment after the step has run.",
        )


class PullCommand(_LifecycleStepCommand):
    """Command to pull parts."""

    name = "pull"
    help_msg = "Download or retrieve artifacts defined for a part"
    overview = textwrap.dedent(
        """
        Download or retrieve artifacts defined for a part. If part names
        are specified only those parts will be pulled, otherwise all parts
        will be pulled.
        """
    )


class OverlayCommand(_LifecycleStepCommand):
    """Command to overlay parts."""

    name = "overlay"
    help_msg = "Create part layers over the base filesystem."
    overview = textwrap.dedent(
        """
        Execute operations defined for each part on a layer over the base
        filesystem, potentially modifying its contents.
        """
    )


class BuildCommand(_LifecycleStepCommand):
    """Command to build parts."""

    name = "build"
    help_msg = "Build artifacts defined for a part"
    overview = textwrap.dedent(
        """
        Build artifacts defined for a part. If part names are specified only
        those parts will be built, otherwise all parts will be built.
        """
    )


class StageCommand(_LifecycleStepCommand):
    """Command to stage parts."""

    name = "stage"
    help_msg = "Stage built artifacts into a common staging area"
    overview = textwrap.dedent(
        """
        Stage built artifacts into a common staging area. If part names are
        specified only those parts will be staged. The default is to stage
        all parts.
        """
    )


class PrimeCommand(_LifecycleStepCommand):
    """Command to prime parts."""

    name = "prime"
    help_msg = "Prime artifacts defined for a part"
    overview = textwrap.dedent(
        """
        Prepare the final payload to be packed as a snap, performing additional
        processing and adding metadata files. If part names are specified only
        those parts will be primed. The default is to prime all parts.
        """
    )


class PackCommand(_LifecycleCommand):
    """Command to pack the final artifact."""

    name = "pack"
    help_msg = "Build artifacts defined for a part"
    overview = textwrap.dedent(
        """
        Prepare the final payload to be packed as a ROCK. If part names are
        specified only those parts will be primed. The default is to prime
        all parts.
        """
    )


class InitCommand(_LifecycleCommand):
    """Initialize a rockcraft project."""

    name = "init"
    help_msg = "Initialize a rockcraft project"
    overview = textwrap.dedent(
        """
        Initialize a rockcraft project by creating a minimalist,
        yet functional, rockcraft.yaml file in the current directory.
        """
    )

    _INIT_TEMPLATE_YAML = textwrap.dedent(
        """\
            name: my-rock-name # the name of your ROCK
            base: ubuntu:22.04 # the base environment for this ROCK
            version: '0.1' # just for humans. Semantic versioning is recommended
            summary: Single-line elevator pitch for your amazing ROCK # 79 char long summary
            description: |
                This is my my-rock-name's description. You have a paragraph or two to tell the
                most important story about it. Keep it under 100 words though,
                we live in tweetspace and your description wants to look good in the
                container registries out there.
            license: GPL-3.0 # your application's SPDX license
            platforms: # The platforms this ROCK should be built on and run on
                amd64:

            parts:
                my-part:
                    plugin: nil
            """
    )

    @overrides
    def run(self, parsed_args):
        """Run the command."""
        lifecycle.init(self._INIT_TEMPLATE_YAML)
