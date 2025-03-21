# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2025 Canonical Ltd.
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

"""Constants for extensions."""

_PYTHON_3_10 = "3.10"
_PYTHON_3_12 = "3.12"

UBUNTU_PYTHON_VERSION_MAP = {
    "ubuntu@22.04": _PYTHON_3_10,
    "ubuntu:22.04": _PYTHON_3_10,
    "ubuntu@24.04": _PYTHON_3_12,
    "ubuntu:24.04": _PYTHON_3_12,
}
