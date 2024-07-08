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

"""An extension for Go based applications."""

import os
import re
from typing import Any, Dict, Tuple

from overrides import override

from ..errors import ExtensionError
from .extension import Extension


class GoFramework(Extension):
    """An extension class for Go applications."""

    @staticmethod
    @override
    def get_supported_bases() -> Tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@22.04", "ubuntu:22.04"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:
        """Check if the extension is in an experimental state."""
        return True

    @override
    def get_root_snippet(self) -> dict[str, Any]:
        """Return the root snippet to apply."""
        self._check_project()

        snippet: Dict[str, Any] = {
            "run_user": "_daemon_",
            "services": {
                "go": {
                    "override": "replace",
                    "startup": "enabled",
                    "command": self.project_name,
                    "user": "_daemon_",
                },
            },
        }

        snippet["parts"] = {
            "go-framework/install-app": self._gen_install_app_part(),
            "go-framework/runtime": {
                "plugin": "nil",
                "stage-packages": ["ca-certificates_data"],
            },
        }

        assets_part = self._gen_install_assets_part()
        if assets_part:
            snippet["parts"]["go-framework/assets"] = assets_part

        return snippet

    @property
    def project_name(self):
        """Return the normalized name of the rockcraft project."""
        return self.yaml_data["name"]

    @property
    def install_app_part(self):
        """Return the install app part for the Go project."""
        if (
            "parts" in self.yaml_data
            and "go-framework/install-app" in self.yaml_data["parts"]
        ):
            self.yaml_data["parts"]["go-framework/install-app"]

    def _gen_install_assets_part(self):
        # if stage is not in exclude mode, use it to generate organize
        if (
            self._assets_stage
            and self._assets_stage[0]
            and self._assets_stage[0][0] != "-"
        ):
            renaming_map = {
                os.path.relpath(file, "go"): file for file in self._assets_stage
            }
        else:
            return None

        return {
            "plugin": "dump",
            "source": ".",
            "organize": renaming_map,
            "stage": self._assets_stage,
        }

    @property
    def _assets_stage(self):
        """Return the assets stage list for the Go project."""
        user_stage = (
            self.yaml_data.get("parts", {})
            .get("go-framework/assets", {})
            .get("stage", [])
        )
        if not all(re.match("-? *go/", p) for p in user_stage):
            raise ExtensionError(
                "go-framework extension requires the 'stage' entry in the "
                "go-framework/assets part to start with go",
                docs_url="https://documentation.ubuntu.com/rockcraft/en/stable/reference/extensions/go-framework",
                logpath_report=False,
            )
        if not user_stage:
            user_stage = [
                f"go/{f}"
                for f in (
                    "migrate",
                    "migrate.sh",
                    "static",
                    "templates",
                )
                if (self.project_root / f).exists()
            ]
        return user_stage

    def _get_nested(self, obj: dict, path: str) -> dict:
        """Get a nested object using a path (a dot-separated list of keys)."""
        for key in path.split("."):
            obj = obj.get(key, {})
        return obj

    def _check_go_overriden(self):
        build_snaps = self._get_nested(
            self.yaml_data, "parts.go-framework/install-app.build-snaps"
        )
        if build_snaps:
            for snap in build_snaps:
                if snap.startswith("go"):
                    return True
        build_packages = self._get_nested(
            self.yaml_data, "parts.go-framework/install-app.build-packages"
        )
        if build_packages:
            for package in build_packages:
                if package in ["gccgo-go", "golang-go"]:
                    return True
        return False

    def _gen_install_app_part(self):
        install_app = self._get_nested(self.yaml_data, "parts.go-framework/install-app")

        build_environment = []
        if self.yaml_data["base"] == "bare":
            for env_var in build_environment:
                if "CGO_ENABLED" in env_var:
                    break
            else:
                build_environment = [{"CGO_ENABLED": "0"}]

        organize = {}
        if "organize" in install_app:
            organize = install_app["organize"]

        binary_path = f"usr/local/bin/{self.project_name}"
        for path in organize.values():
            if path == binary_path:
                break
        else:
            if not self._get_nested(self.yaml_data, "services.go.command"):
                organize[f"bin/{self.project_name}"] = binary_path

        install_app_part = {
            "plugin": "go",
            "source": ".",
            "build-snaps": [] if self._check_go_overriden() else ["go"],
            "organize": organize,
        }

        install_app_part["stage"] = [val for val in organize.values()]
        if build_environment:
            install_app_part["build-environment"] = build_environment

        return install_app_part

    def _check_project(self):
        if not (self.project_root / "go.mod").exists():
            raise ExtensionError(
                "missing go.mod file",
                docs_url="https://documentation.ubuntu.com/rockcraft/en/stable/reference/extensions/go-framework",
                logpath_report=False,
            )

    @override
    def get_parts_snippet(self) -> dict[str, Any]:
        """Return the parts to add to parts."""
        return {}

    @override
    def get_part_snippet(self) -> dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}
