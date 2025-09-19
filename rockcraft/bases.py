# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021,2024 Canonical Ltd.
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

"""Definitions of supported bases, and per-base behaviors."""

SUPPORTED = (
    "ubuntu@20.04",
    "ubuntu@22.04",
    "ubuntu@24.04",
    "ubuntu@25.10",
)
"""Ubuntu bases currently supported by Rockcraft."""

#############################
# Pebble-related definitions
#############################

PEBBLE_IN_BIN = ("ubuntu@20.04", "ubuntu@22.04")
"""Bases where the Pebble binary exists as "/bin/pebble"."""

PEBBLE_ORGANIZED_USR_BIN = ("ubuntu@24.04",)
"""Bases where the Pebble binary is organized to /usr/bin/pebble."""

###########################################
# Plugin and Lifecycle-related definitions
###########################################

PRE_USRMERGED_INSTALL = ("ubuntu@20.04", "ubuntu@22.04", "ubuntu@24.04")
"""Bases where we *don't* usrmerge a part's install dir by default."""

PYTHON_PRE_BAD_LIB64 = ("ubuntu@20.04", "ubuntu@22.04")
"""Bases where we *didn't* have to manually fix the venv-provided "lib64" symlink."""
