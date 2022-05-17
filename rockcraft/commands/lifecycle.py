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

from craft_cli import BaseCommand
from overrides import overrides

from rockcraft import lifecycle


class _LifecycleCommand(BaseCommand, abc.ABC):
    """Run lifecycle-related commands."""


class PackCommand(_LifecycleCommand):
    """Prepare the final payload for packing."""

    name = "pack"
    help_msg = "Build artifacts defined for a part"
    overview = textwrap.dedent(
        """
        Prepare the final payload to be packed as a ROCK. If part names are
        specified only those parts will be primed. The default is to prime
        all parts.
        """
    )

    @overrides
    def run(self, parsed_args):
        """Run the command."""
        lifecycle.pack()


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
            name: my-rock-name
            base: ubuntu:20.04 # the base environment for this ROCK
            version: '0.1' # just for humans, typically '1.2+git' or '1.3.2'
            title: My ROCK Title Name # a human-friendly title for your ROCK
            summary: Single-line elevator pitch for your amazing ROCK # 79 char long summary
            description: |
                This is a long description of the ROCK. You have a paragraph or two to tell the
                most important story about it. Keep it under 100 words though,
                we live in tweetspace and your description wants to look good in the 
                container registries out there.

            license: Change-Me # your application's license, in SPDX format
            
            parts:
                my-part:
                    plugin: nil
            """
    )

    @overrides
    def run(self, parsed_args):
        """Run the command."""
        lifecycle.init(self._INIT_TEMPLATE_YAML)
