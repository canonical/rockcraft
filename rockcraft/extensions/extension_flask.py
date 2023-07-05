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

"""An experimental extension for the Juju PaaS Flask framework."""

import os

from typing import Tuple, Dict, Any, Optional
from overrides import override

from .extension import Extension


class FlaskExtension(Extension):
    """An extension to enable Flask support within the Juju PaaS ecosystem.

    This extension is a part of the Juju PaaS ecosystem and facilitates the deployment of
    Flask-based applications.
    """

    @staticmethod
    @override
    def get_supported_bases() -> Tuple[str, ...]:
        return "bare", "ubuntu:22.04"

    @staticmethod
    @override
    def is_experimental(base: Optional[str]) -> bool:
        return True

    @override
    def get_root_snippet(self) -> Dict[str, Any]:
        """Fill in some default root components for Flask.

        Default values:
          - run_user: _daemon_
          - build-base: ubuntu:22.04 (only if user specify bare without a build-base)
          - platform: amd64
        """
        snippet = {}
        if "run_user" not in self.yaml_data:
            snippet["run_user"] = "_daemon_"
        if (
                "build-base" not in self.yaml_data and
                self.yaml_data.get("base", "bare") == "bare"
        ):
            snippet["build-base"] = "ubuntu:22.04"
        if "platforms" not in self.yaml_data:
            snippet["platforms"] = {"amd64": {}}
        return snippet

    @override
    def get_part_snippet(self) -> Dict[str, Any]:
        return {}

    @override
    def get_parts_snippet(self) -> Dict[str, Any]:
        """Create necessary parts to facilitate the flask application.

        Parts added:
            - flask-extension/dependencies: install Python dependencies
            - flask-extension/install-app: copy the flask project into the OCI image
        """
        python_requirements = []
        if (self.project_root / "requirements.txt").exists():
            python_requirements.append("requirements.txt")
        ignores = [".git", "node_modules"]
        source_files = [
            f for f in os.listdir(self.project_root)
            if f not in ignores and not f.endswith(".rock")
        ]
        renaming_map = {
            f: os.path.join("srv/flask/app", f)
            for f in source_files
        }
        snippet = {
            "flask-extension/dependencies": {
                "plugin": "python",
                "stage-packages": ["python3-venv"],
                "source": ".",
                "python-packages": ["gunicorn"],
                "python-requirements": python_requirements
            },
            "flask-extension/install-app": {
                "plugin": "dump",
                "source": ".",
                "organize": renaming_map,
                "stage": list(renaming_map.values())
            }
        }
        return snippet
