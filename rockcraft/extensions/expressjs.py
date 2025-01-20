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
                    "environment": {
                        "NODE_ENV": "production",
                    },
                }
            },
        }
        if not self.yaml_data.get("services", {}).get("expressjs", {}).get("command"):
            snippet["services"]["expressjs"]["command"] = "npm start"

        snippet["parts"] = {
            "expressjs-framework/install-app": self._gen_install_app_part(),
            "expressjs-framework/runtime": self._gen_runtime_part(),
        }
        return snippet

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

    def _gen_install_app_part(self) -> dict:
        """Generate the install app part using NPM plugin."""
        install_app_part: dict[str, Any] = {
            "plugin": "npm",
            "source": f"{self.IMAGE_BASE_DIR}/",
            "build-packages": self._install_app_build_packages,
            "stage-packages": self._install_app_stage_packages,
            "override-build": (
                "craftctl default\n"
                "npm config set script-shell=bash --location project\n"
                "cp ${CRAFT_PART_BUILD}/.npmrc ${CRAFT_PART_INSTALL}/lib/node_modules/"
                f"{self._app_name}/.npmrc\n"
                f"ln -s /lib/node_modules/{self._app_name} ${{CRAFT_PART_INSTALL}}/app\n"
            ),
        }
        if self._user_npm_include_node:
            install_app_part["npm-include-node"] = self._user_npm_include_node
            install_app_part["npm-node-version"] = self._user_install_app_part.get(
                "npm-node-version"
            )
        return install_app_part

    @property
    def _install_app_build_packages(self) -> list[str]:
        """Return the build packages for the install app part."""
        if self._user_npm_include_node:
            return []
        return ["nodejs", "npm"]

    @property
    def _install_app_stage_packages(self) -> list[str]:
        """Return the stage packages for the install app part."""
        if self._rock_base == "bare":
            return [
                "bash_bins",
                "ca-certificates_data",
                "nodejs_bins",
                "coreutils_bins",
            ]
        if not self._user_npm_include_node:
            return ["ca-certificates_data", "nodejs_bins"]
        return ["ca-certificates_data"]

    def _gen_runtime_part(self) -> dict:
        """Generate the runtime part."""
        runtime_part: dict[str, Any] = {
            "plugin": "nil",
            "stage-packages": [] if self._user_npm_include_node else ["npm"],
        }
        return runtime_part

    @property
    def _user_install_app_part(self) -> dict:
        """Return the user defined install app part."""
        return self.yaml_data.get("parts", {}).get(
            "expressjs-framework/install-app", {}
        )

    @property
    def _user_npm_include_node(self) -> bool:
        """Return the user defined npm include node flag."""
        return self._user_install_app_part.get("npm-include-node", False)

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
