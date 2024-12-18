# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2024 Canonical Ltd.
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

"""An extension for the NodeJS based Javascript application extension."""
from typing import Any, Dict, Tuple

from overrides import override

from .extension import Extension


class ExpressJSFramework(Extension):
    """An extension for constructing Javascript applications based on the ExpressJS framework."""

    @staticmethod
    @override
    def get_supported_bases() -> Tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@22.04", "ubuntu:22.04", "ubuntu@24.04", "ubuntu:24.04"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:
        """Check if the extension is in an experimental state."""
        return False

    @property
    @override
    def framework(self) -> str:
        """Return the framework name, i.e. expressjs."""
        return "expressjs"

    @override
    def get_root_snippet(self) -> Dict[str, Any]:
        """Fill in some default root components.

        Default values:
          - run_user: _daemon_
          - build-base: ubuntu:22.04 (only if user specify bare without a build-base)
          - platform: amd64
          - services: a service to run the ExpressJS server
          - parts: see ExpressJSFramework._gen_parts
        """
        snippet: Dict[str, Any] = {
            "run-user": "_daemon_",
            "services": {
                "app": {
                    "override": "replace",
                    "command": "npm start",
                    "startup": "enabled",
                    "on-success": "shutdown",
                    "on-failure": "shutdown",
                    "working-dir": "/lib/node_modules/expressjs-project",
                }
            },
        }
        return snippet

    @override
    def get_part_snippet(self) -> dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}

    @override
    def get_parts_snippet(self) -> dict[str, Any]:
        """Return the parts to add to parts."""
        return {}

    def _gen_parts(self) -> dict:
        """Generate the parts associated with this extension."""
        ...

    def _check_project(self):
        """Ensure this extension can apply to the current rockcraft project.

        The ExpressJS framework assumes that:
        - The npm start script exists.
        """
        ...
