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

    IMAGE_BASE_DIR = "app"

    @staticmethod
    @override
    def get_supported_bases() -> tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@24.04"

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
          - build-base: ubuntu:24.04
          - platform: amd64
          - services: a service to run the ExpressJS server
          - parts: see ExpressJSFramework._gen_parts
        """
        self._check_project()

        snippet: dict[str, Any] = {
            "run-user": "_daemon_",
            "services": {
                "expressjs": {
                    "override": "replace",
                    "startup": "enabled",
                    "user": "_daemon_",
                    "working-dir": f"/{self.IMAGE_BASE_DIR}",
                }
            },
        }
        if not self.yaml_data.get("services", {}).get("expressjs", {}).get("command"):
            snippet["services"]["expressjs"]["command"] = "npm start"

        snippet["parts"] = {
            "expressjs-framework/install-app": self._gen_install_app_part()
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
        runtime_packages = ["ca-certificates_data"]
        if self._rock_base == "bare":
            runtime_packages += [
                "bash_bins",
                "coreutils_bins",
                "libc6_libs",
                "libnode109_libs",
            ]
        return {
            "plugin": "npm",
            "npm-include-node": True,
            "npm-node-version": self._install_app_node_version,
            "source": "app/",
            "organize": self._app_organize,
            "override-build": (
                "craftctl default\n"
                "npm config set script-shell=bash --location project\n"
                "cp ${CRAFT_PART_BUILD}/.npmrc ${CRAFT_PART_INSTALL}/lib/node_modules/"
                f"{self._app_name}/.npmrc"
            ),
            "override-prime": (
                "craftctl default\n"
                f"rm -rf ${{CRAFT_PRIME}}/lib/node_modules/{self._app_name}\n"
            ),
            "stage-packages": runtime_packages,
        }

    @property
    def _rock_base(self) -> str:
        """Return the base of the rockcraft project."""
        return self.yaml_data["base"]

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
    def _user_install_app_part(self) -> dict:
        """Return the user defined install app part."""
        return self.yaml_data.get("parts", {}).get(
            "expressjs-framework/install-app", {}
        )

    @property
    def _app_organize(self) -> dict:
        """Return the organized mapping for the ExpressJS project.

        Use the paths generated by the
        express-generator (https://expressjs.com/en/starter/generator.html) tool by default if no
        user prime paths are provided. Use only user prime paths otherwise.
        """
        user_prime: list[str] = self._user_install_app_part.get("prime", [])

        if not all(re.match(f"-? *{self.IMAGE_BASE_DIR}/", p) for p in user_prime):
            raise ExtensionError(
                "expressjs-framework extension requires the 'prime' entry in the "
                f"expressjs-framework/install-app part to start with {self.IMAGE_BASE_DIR}",
                doc_slug="/reference/extensions/expressjs-framework",
                logpath_report=False,
            )
        if not user_prime:
            # default paths generated by express-generator
            user_prime = [
                "bin",
                "public",
                "routes",
                "views",
                "app.js",
            ]

        project_relative_file_paths = [
            prime_path.removeprefix(f"{self.IMAGE_BASE_DIR}/")
            for prime_path in [*user_prime, "package.json", "package-lock.json"]
        ]
        lib_dir = f"lib/node_modules/{self._app_name}"
        organize_mappings = {
            f"{lib_dir}/{f}": f"{self.IMAGE_BASE_DIR}/{f}"
            for f in project_relative_file_paths
            if (self.project_root / self.IMAGE_BASE_DIR / f).exists()
        }
        for build_artifact in ["node_modules", ".npmrc"]:
            organize_mappings[f"{lib_dir}/{build_artifact}"] = (
                f"{self.IMAGE_BASE_DIR}/{build_artifact}"
            )

        return organize_mappings

    @property
    def _install_app_node_version(self) -> str:
        node_version = self._user_install_app_part.get("npm-node-version", "node")
        if not node_version:
            return "node"
        return node_version

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
