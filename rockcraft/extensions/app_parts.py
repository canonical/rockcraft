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

"""Common extension application parts."""


def gen_logging_part(
    override_build_lines: list[str] | None = None, permissions: list[dict] | None = None
) -> dict:
    """Generate a logging part for the application."""
    _override_build_lines = [
        "craftctl default",
        "mkdir -p $CRAFT_PART_INSTALL/opt/promtail",
        "mkdir -p $CRAFT_PART_INSTALL/etc/promtail",
    ]
    if override_build_lines:
        _override_build_lines.extend(override_build_lines)
    _permissions = [
        {"path": "opt/promtail", "owner": 584792, "group": 584792},
        {"path": "etc/promtail", "owner": 584792, "group": 584792},
    ]
    if permissions:
        _permissions.extend(permissions)

    return {
        "plugin": "nil",
        "override-build": "\n".join(_override_build_lines),
        "permissions": _permissions,
    }
