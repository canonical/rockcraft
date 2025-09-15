# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
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

"""Pebble metadata and configuration helpers."""

from typing import Any

from craft_application.errors import CraftValidationError
from craft_cli import emit


def add_apt_update_part(project: dict[str, Any]) -> None:
    """Add hidden part to execute apt-get upgrade in an overlay."""
    part_name = "_apt-upgrade"
    part_content = {
        "plugin": "nil",
        "overlay-script": 'craftctl chroot bash -c "'
        "apt-get update && "
        "apt-get -y upgrade && "
        "apt-get clean && "
        "rm -rf /var/lib/apt/lists/*"
        '"',
    }

    parts = project.get("parts", {})

    if project.get("base") == "bare":
        # Skip adding the part to bare projects as executing apt-get upgrade
        # would not make sense without a Ubuntu base.
        emit.progress(
            f"project base is 'bare', skipping adding the '{part_name}' part."
        )
        return

    if not parts:
        # Invalid project: let it return to fail in the regular validation flow.
        return

    if (
        existing_part_content := parts.get(part_name)
    ) is not None and existing_part_content != part_content:
        raise CraftValidationError(f'Cannot override the default "{part_name}" part.')

    parts[part_name] = part_content
