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

from typing import Any

from rockcraft.usernames import SUPPORTED_GLOBAL_USERNAMES

from .extension import Extension

USER_UID: int = SUPPORTED_GLOBAL_USERNAMES["_daemon_"]["uid"]


class AppDataDirMixin(Extension):
    """Add the writable application data directory used by v2 frameworks."""

    def get_root_snippet(self) -> dict[str, Any]:
        """Add the shared application data part to the framework snippet."""
        snippet = super().get_root_snippet()
        snippet["parts"]["app-data"] = {
            "plugin": "nil",
            "override-build": "mkdir -p ${CRAFT_PART_INSTALL}/app-data",
            "permissions": [{"path": "app-data", "owner": USER_UID, "group": USER_UID}],
        }
        return snippet


def gen_logging_part(
    override_build_lines: list[str] | None = None,
    permissions: list[dict[str, str | int]] | None = None,
) -> dict[str, str | list[dict[str, str | int]]]:
    """Generate a logging part for the application."""
    _override_build_lines = [
        "craftctl default",
        "mkdir -p $CRAFT_PART_INSTALL/opt/promtail",
        "mkdir -p $CRAFT_PART_INSTALL/etc/promtail",
    ]
    if override_build_lines:
        _override_build_lines.extend(override_build_lines)
    _permissions: list[dict[str, str | int]] = [
        {"path": "opt/promtail", "owner": USER_UID, "group": USER_UID},
        {"path": "etc/promtail", "owner": USER_UID, "group": USER_UID},
    ]
    if permissions:
        _permissions.extend(permissions)

    return {
        "plugin": "nil",
        "override-build": "\n".join(_override_build_lines),
        "permissions": _permissions,
    }
