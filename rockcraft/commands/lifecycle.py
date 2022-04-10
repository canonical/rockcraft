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
        Prepare the final payload to be packed as a snap. If part names are
        specified only those parts will be primed. The default is to prime
        all parts.
        """
    )

    @overrides
    def run(self, parsed_args):
        """Run the command."""
        lifecycle.pack()
