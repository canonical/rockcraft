#  This file is part of Rockcraft.
#
#  Copyright 2023 Canonical Ltd.
#
#  This program is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License version 3, as
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
#  SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program.  If not, see <http://www.gnu.org/licenses/>.
import os

import pytest


@pytest.fixture
def overlay_mocks(mocker):
    """Mock overlay-related calls that are not relevant to the test but happen anyway."""

    # Mock some overlay-related calls
    # Mock calls to chroot that come from the 'hidden' part that upgrades the overlay
    # system
    mocker.patch("craft_parts.overlays.chroot.chroot")

    # Mock os.geteuid() because currently craft-parts doesn't allow overlays
    # without superuser privileges.
    mocker.patch.object(os, "geteuid", return_value=0)
