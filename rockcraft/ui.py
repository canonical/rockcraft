#!/usr/bin/env python3
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2021 Canonical Ltd
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

"""User interface for Rockcraft."""

from craft_cli.errors import CraftError
from craft_cli.messages import Emitter, EmitterMode

import rockcraft

emit = Emitter()


def init(argv) -> None:
    """Initialize the Command Line Interface from argv."""
    emitter_mode = EmitterMode.NORMAL

    try:
        if len(argv) < 2 or argv[1] != "pack":
            raise CraftError("Only pack is supported.")

        if len(argv) == 3 and argv[2] == "--verbose":
            emitter_mode = EmitterMode.VERBOSE
        elif len(argv) == 3 and argv[2] != "--verbose":
            raise CraftError("Only option supported for pack is '--verbose'.")
    finally:
        emit.init(
            emitter_mode, "rockcraft", f"Rockcraft version {rockcraft.__version__}."
        )
