# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2021 Canonical Ltd.
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

"""Craft-parts lifecycle."""
from typing import Any

import craft_parts


def validate_part(data: dict[str, Any]) -> None:
    """Validate the given part data against common and plugin models.

    :param data: The part data to validate.
    """
    craft_parts.validate_part(data)


def part_has_overlay(data: dict[str, Any]) -> bool:
    """Whether ``data`` declares an overlay-using part."""
    return craft_parts.part_has_overlay(data)
