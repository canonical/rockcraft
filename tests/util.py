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
import pytest
from craft_parts import errors
from craft_parts.utils import os_utils


def is_ubuntu_jammy() -> bool:
    release = os_utils.OsRelease()
    try:
        return release.id() == "ubuntu" and release.version_id() == "22.04"
    except errors.OsReleaseIdError:
        return False


jammy_only = pytest.mark.skipif(
    not is_ubuntu_jammy(), reason="platform must be Ubuntu Jammy"
)
