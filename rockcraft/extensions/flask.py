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

"""An experimental extension for the Flask framework."""

import os
from typing import Any, Dict, Optional, Tuple

from overrides import override

from .extension import Extension


class Flask(Extension):
    """An extension for constructing Python applications based on the Flask framework."""

    @staticmethod
    @override
    def get_supported_bases() -> Tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu:20.04", "ubuntu:22.04"

    @staticmethod
    @override
    def is_experimental(base: Optional[str]) -> bool:
        """Check if the extension is in an experimental state."""
        return True

    @override
    def get_root_snippet(self) -> Dict[str, Any]:
        """Fill in some default root components for Flask.

        Default values:
          - run_user: _daemon_
          - build-base: ubuntu:22.04 (only if user specify bare without a build-base)
          - platform: amd64
        """
        snippet: Dict[str, Any] = {}
        if "run_user" not in self.yaml_data:
            snippet["run_user"] = "_daemon_"
        if (
            "build-base" not in self.yaml_data
            and self.yaml_data.get("base", "bare") == "bare"
        ):
            snippet["build-base"] = "ubuntu:22.04"
        if "platforms" not in self.yaml_data:
            snippet["platforms"] = {"amd64": {}}
        return snippet

    @override
    def get_part_snippet(self) -> Dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}

    @override
    def get_parts_snippet(self) -> Dict[str, Any]:
        """Create necessary parts to facilitate the flask application.

        Parts added:
            - flask/dependencies: install Python dependencies
            - flask/install-app: copy the flask project into the OCI image
        """
        if not (self.project_root / "requirements.txt").exists():
            raise ValueError(
                "missing requirements.txt file, "
                "flask extension requires this file with flask specified as a dependency"
            )
        ignores = [".git", "node_modules", ".yarn"]
        source_files = [
            f
            for f in os.listdir(self.project_root)
            if f not in ignores and not f.endswith(".rock")
        ]
        renaming_map = {f: os.path.join("srv/flask/app", f) for f in source_files}
        snippet = {
            "flask/dependencies": {
                "plugin": "python",
                "stage-packages": ["python3-venv"],
                "source": ".",
                "python-packages": ["gunicorn"],
                "python-requirements": ["requirements.txt"],
            },
            # Users are required to compile any static assets prior to executing the
            # rockcraft pack command, so assets can be included in the final OCI image.
            "flask/install-app": {
                "plugin": "dump",
                "source": ".",
                "organize": renaming_map,
                "stage": list(renaming_map.values()),
            },
        }
        return snippet
