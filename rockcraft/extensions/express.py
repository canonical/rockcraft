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
import json
import re
from typing import Any, Dict, Tuple

from overrides import override

from ..errors import ExtensionError
from .extension import Extension


class ExpressJSFramework(Extension):
    """An extension for constructing Javascript applications based on the ExpressJS framework."""

    IMAGE_BASE_DIR = "app"
    EXPRESS_GENERATOR_DIRS = (
        "bin",
        "public",
        "routes",
        "views",
        "app.js",
        "package.json",
        "package-lock.json",
        "node_modules",
    )
    RUNTIME_DEPENDENCIES = ["ca-certificates_data", "libpq5", "node"]

    @staticmethod
    @override
    def get_supported_bases() -> Tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@22.04", "ubuntu@24.04"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:
        """Check if the extension is in an experimental state."""
        return True

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
        self._check_project()

        snippet: Dict[str, Any] = {
            "run-user": "_daemon_",
            "services": {
                "app": {
                    "override": "replace",
                    "command": "npm start",
                    "startup": "enabled",
                    "on-success": "shutdown",
                    "on-failure": "shutdown",
                    "working-dir": "/app",
                }
            },
        }

        snippet["parts"] = {
            "expressjs-framework/install-app": self._gen_install_app_part(),
            "expressjs-framework/runtime-dependencies": self._gen_runtime_dependencies_part(),
        }
        return snippet

    @override
    def get_part_snippet(self) -> dict[str, Any]:
        """Return the part snippet to apply to existing parts.

        This is unused but is required by the ABC.
        """
        return {}

    @override
    def get_parts_snippet(self) -> dict[str, Any]:
        """Return the parts to add to parts.

        This is unused but is required by the ABC.
        """
        return {}

    def _gen_install_app_part(self) -> dict:
        """Generate the install app part using NPM plugin."""
        return {
            "plugin": "npm",
            "npm-include-node": False,
            "source": "app/",
            "organise": self._app_organise,
            "override-prime": f"rm -rf lib/node_modules/{self._app_name}",
        }

    def _gen_runtime_dependencies_part(self) -> dict:
        """Generate the install dependencies part using dump plugin."""
        return {
            "plugin": "nil",
            "stage-packages": self.RUNTIME_DEPENDENCIES,
        }

    @property
    def _app_package_json(self):
        """Return the app package.json contents."""
        package_json_file = self.project_root / "package.json"
        if not package_json_file.exists():
            raise ExtensionError(
                "missing package.json file",
                doc_slug="/reference/extensions/expressjs-framework",
                logpath_report=False,
            )
        package_json_contents = package_json_file.read_text(encoding="utf-8")
        return json.loads(package_json_contents)

    @property
    def _app_name(self) -> str:
        """Return the application name as defined on package.json."""
        return self._app_package_json["name"]

    @property
    def _app_organise(self):
        """Return the organised mapping for the ExpressJS project.

        Use the paths generated by the
        express-generator (https://expressjs.com/en/starter/generator.html) tool by default if no
        user prime paths are provided. Use only user prime paths otherwise.
        """
        user_prime: list[str] = (
            self.yaml_data.get("parts", {})
            .get("expressjs-framework/install-app", {})
            .get("prime", [])
        )
        if not all(re.match(f"-? *{self.IMAGE_BASE_DIR}/", p) for p in user_prime):
            raise ExtensionError(
                "expressjs-framework extension requires the 'prime' entry in the "
                f"expressjs-framework/install-app part to start with {self.IMAGE_BASE_DIR}/",
                doc_slug="/reference/extensions/expressjs-framework",
                logpath_report=False,
            )
        if not user_prime:
            user_prime = [
                f"{self.project_root}/{f}" for f in self.EXPRESS_GENERATOR_DIRS
            ]
        lib_dir = f"lib/node_modules/{self._app_name}"
        return {
            f"{lib_dir}/{f}": f"app/{f}"
            for f in user_prime
            if (self.project_root / f).exists()
        }

    def _check_project(self):
        """Ensure this extension can apply to the current rockcraft project.

        The ExpressJS framework assumes that:
        - The npm start script exists.
        - The application name is defined.
        """
        if (
            "scripts" not in self._app_package_json
            or "start" not in self._app_package_json["scripts"]
            or "name" not in self._app_package_json
        ):
            raise ExtensionError(
                "missing start script",
                doc_slug="/reference/extensions/expressjs-framework",
                logpath_report=False,
            )
