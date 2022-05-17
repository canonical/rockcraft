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

    @overrides
    def run(self, parsed_args):
        """Run the command."""
        
        _TEMPLATE_YAML = textwrap.dedent(
            """\
            name: my-snap-name # you probably want to 'snapcraft register <name>'
            base: core20 # the base snap is the execution environment for this snap
            version: '0.1' # just for humans, typically '1.2+git' or '1.3.2'
            summary: Single-line elevator pitch for your amazing snap # 79 char long summary
            description: |
            This is my-snap's description. You have a paragraph or two to tell the
            most important story about your snap. Keep it under 100 words though,
            we live in tweetspace and your description wants to look good in the snap
            store.

            grade: devel # must be 'stable' to release into candidate/stable channels
            confinement: devmode # use 'strict' once you have the right plugs and slots

            parts:
            my-part:
                # See 'snapcraft plugins'
                plugin: nil
            """
        )
        
        lifecycle.init(_TEMPLATE_YAML)
