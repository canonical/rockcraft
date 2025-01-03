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
from typing import Any

from overrides import override

from ..errors import ExtensionError
from .extension import Extension


class ExpressJSFramework(Extension):
    """An extension for constructing Javascript applications based on the ExpressJS framework."""

    IMAGE_BASE_DIR = "app/"
    EXPRESS_GENERATOR_DIRS = [
        "bin",
        "public",
        "routes",
        "views",
        "app.js",
    ]
    EXPRESS_PACKAGE_DIRS = [
        "package.json",
        "package-lock.json",
        "node_modules",
    ]
    RUNTIME_DEBS = ["ca-certificates_data"]
    RUNTIME_SLICES = ["node", "libpq5"]

    @staticmethod
    @override
    def get_supported_bases() -> tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@22.04", "ubuntu@24.04"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:
        """Check if the extension is in an experimental state."""
        return True

    @override
    def get_root_snippet(self) -> dict[str, Any]:
        """Fill in some default root components.

        Default values:
          - run_user: _daemon_
          - build-base: ubuntu:22.04 (only if user specify bare without a build-base)
          - platform: amd64
          - services: a service to run the ExpressJS server
          - parts: see ExpressJSFramework._gen_parts
        """
        self._check_project()

        snippet: dict[str, Any] = {
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
            "expressjs-framework/runtime-debs": self._gen_runtime_debs_part(),
            "expressjs-framework/runtime-slices": self._gen_runtime_slices_part(),
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
            "organize": self._app_organize,
            "override-prime": f"rm -rf lib/node_modules/{self._app_name}",
            "build-packages": ["nodejs"],
        }

    def _gen_runtime_debs_part(self) -> dict:
        """Generate the runtime debs part."""
        return {
            "plugin": "nil",
            "stage-packages": self.RUNTIME_DEBS,
        }

    def _gen_runtime_slices_part(self) -> dict:
        """Generate the runtime slices part."""
        # Runtime slices have been separated from runtime debs since rockcraft does not support
        # mixing the two. See https://github.com/canonical/rockcraft/issues/183.
        return {"plugin": "nil", "stage-packages": self.RUNTIME_SLICES}

    @property
    def _app_package_json(self) -> dict:
        """Return the app package.json contents."""
        package_json_file = self.project_root / self.IMAGE_BASE_DIR / "package.json"
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
    def _app_organize(self) -> dict:
        """Return the organized mapping for the ExpressJS project.

        Use the paths generated by the
        express-generator (https://expressjs.com/en/starter/generator.html) tool by default if no
        user prime paths are provided. Use only user prime paths otherwise.
        """
        user_prime: list[str] = (
            self.yaml_data.get("parts", {})
            .get("expressjs-framework/install-app", {})
            .get("prime", [])
        )
        if not all(re.match(f"-? *{self.IMAGE_BASE_DIR}", p) for p in user_prime):
            raise ExtensionError(
                "expressjs-framework extension requires the 'prime' entry in the "
                f"expressjs-framework/install-app part to start with {self.IMAGE_BASE_DIR}",
                doc_slug="/reference/extensions/expressjs-framework",
                logpath_report=False,
            )
        if not user_prime:
            user_prime = self.EXPRESS_GENERATOR_DIRS
        project_relative_file_paths = [
            prime_path.removeprefix(self.IMAGE_BASE_DIR)
            for prime_path in user_prime + self.EXPRESS_PACKAGE_DIRS
        ]
        lib_dir = f"lib/node_modules/{self._app_name}"
        return {
            f"{lib_dir}/{f}": f"app/{f}"
            for f in project_relative_file_paths
            if (self.project_root / "app" / f).exists()
        }

    def _check_project(self) -> None:
        """Ensure this extension can apply to the current rockcraft project.

        The ExpressJS framework assumes that:
        - The npm start script exists.
        - The application name is defined.
        """
        if (
            "scripts" not in self._app_package_json
            or "start" not in self._app_package_json["scripts"]
        ):
            raise ExtensionError(
                "missing start script",
                doc_slug="/reference/extensions/expressjs-framework",
                logpath_report=False,
            )
        if "name" not in self._app_package_json:
            raise ExtensionError(
                "missing application name",
                doc_slug="/reference/extensions/expressjs-framework",
                logpath_report=False,
            )
