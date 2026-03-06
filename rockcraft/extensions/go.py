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
from typing import Any

from overrides import override  # type: ignore[reportUnknownVariableType]

from rockcraft.errors import ExtensionError
from rockcraft.usernames import SUPPORTED_GLOBAL_USERNAMES

from .app_parts import gen_logging_part
from .extension import Extension

USER_UID: int = SUPPORTED_GLOBAL_USERNAMES["_daemon_"]["uid"]


class GoFramework(Extension):
    """An extension class for Go applications."""

    @staticmethod
    @override
    def get_supported_bases() -> tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@24.04"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:  # noqa: ARG004 (unused arg)
        """Check if the extension is in an experimental state."""
        return True

    @override
    def get_root_snippet(self) -> dict[str, Any]:
        """Return the root snippet to apply."""
        self._check_project()

        snippet: dict[str, Any] = {
            "run_user": "_daemon_",
            "services": {
                "go": {
                    "override": "replace",
                    "startup": "enabled",
                    "command": self.project_name,
                    "user": "_daemon_",
                    "working-dir": "/app",
                },
            },
        }

        stage_packages = ["ca-certificates_data"]
        if self.yaml_data["base"] == "bare":
            stage_packages.extend(["bash_bins", "coreutils_bins"])

        snippet["parts"] = {
            # This is needed in case there is no assets part, as the working directory is /app
            "go-framework/base-layout": {
                "plugin": "nil",
                "override-build": "mkdir -p ${CRAFT_PART_INSTALL}/app",
                "permissions": [{"owner": USER_UID, "group": USER_UID}],
            },
            "go-framework/install-app": self._get_install_app_part(),
            "go-framework/runtime": {
                "plugin": "nil",
                "stage-packages": stage_packages,
            },
            "go-framework/logging": gen_logging_part(),
        }

        if self.yaml_data["base"] == "bare":
            snippet["parts"]["go-framework/runtime"].update(
                {
                    "override-build": "ln -sf /usr/bin/bash ${CRAFT_PART_INSTALL}/usr/bin/sh"
                }
            )
        assets_part = self._get_install_assets_part()
        if assets_part:
            snippet["parts"]["go-framework/assets"] = assets_part

        return snippet

    @override
    def get_parts_snippet(self) -> dict[str, Any]:
        """Return the parts to add to parts."""
        return {}

    @override
    def get_part_snippet(self) -> dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}

    @property
    def project_name(self) -> str:
        """Return the normalized name of the rockcraft project."""
        return self.yaml_data["name"]

    def _check_project(self) -> None:
        """Check go.mod file and Go sources exist in project."""
        if not (self.project_root / "go.mod").exists():
            raise ExtensionError(
                "missing go.mod file, it should be present in the project directory",
                doc_slug="/reference/extensions/go-framework/#project-requirements",
                logpath_report=False,
            )

        go_files = list(self.project_root.rglob("*.go"))
        if not go_files:
            raise ExtensionError(
                "No Go source files found. The go-framework extension requires "
                "at least one Go source file (typically with a main package).",
                doc_slug="/reference/extensions/go-framework/#project-requirements",
                logpath_report=False,
            )

    def _get_install_app_part(self) -> dict[str, Any]:
        """Generate install-app part with the Go plugin."""
        install_app = self._get_nested(
            self.yaml_data, ["parts", "go-framework/install-app"]
        )

        build_environment = install_app.get("build-environment", [])
        if self.yaml_data["base"] == "bare":
            for env_var in build_environment:
                if "CGO_ENABLED" in env_var:
                    break
            else:
                build_environment = [{"CGO_ENABLED": "0"}]

        organize = install_app.get("organize", {})
        binary_path = f"usr/local/bin/{self.project_name}"
        for path in organize.values():
            if path == binary_path:
                break
        else:
            if not self._get_nested(self.yaml_data, ["services", "go", "command"]):
                organize[f"bin/{self.project_name}"] = binary_path

        install_app_part = {
            "plugin": "go",
            "source": ".",
            "organize": organize,
        }

        if not self._check_go_overridden():
            build_snaps = install_app.get("build-snaps", [])
            build_snaps.append("go")
            install_app_part["build-snaps"] = build_snaps

        install_app_part["stage"] = list(organize.values())
        if build_environment:
            install_app_part["build-environment"] = build_environment

        return install_app_part

    def _check_go_overridden(self) -> bool:
        """Check if the user overrode the go snap or package for the build step."""
        install_app = self._get_nested(
            self.yaml_data, ["parts", "go-framework/install-app"]
        )
        build_snaps = install_app.get("build-snaps", [])
        if build_snaps:
            for snap in build_snaps:
                if snap.startswith("go"):
                    return True
        build_packages = install_app.get("build-packages", [])
        if build_packages:
            for package in build_packages:
                if package in ["gccgo-go", "golang-go"]:
                    return True
        return False

    def _get_install_assets_part(self) -> dict[str, Any] | None:
        """Generate assets-stage part for extra assets in the project."""
        # if stage is not in exclude mode, use it to generate organize
        if (
            self._assets_stage
            and self._assets_stage[0]
            and self._assets_stage[0][0] != "-"
        ):
            renaming_map = {
                os.path.relpath(file, "app"): file for file in self._assets_stage
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
    def _assets_stage(self) -> list[str]:
        """Return the assets stage list for the Go project."""
        user_stage = self._get_nested(
            self.yaml_data, ["parts", "go-framework/assets"]
        ).get("stage", [])

        if not all(re.match("-? *app/", p) for p in user_stage):
            raise ExtensionError(
                "go-framework extension requires the 'stage' entry in the "
                "go-framework/assets part to start with app",
                doc_slug="/reference/extensions/go-framework",
                logpath_report=False,
            )
        if not user_stage:
            user_stage = [
                f"app/{f}"
                for f in (
                    "migrate",
                    "migrate.sh",
                    "static",
                    "templates",
                )
                if (self.project_root / f).exists()
            ]
        return user_stage

    def _get_nested(self, obj: dict[str, Any], paths: list[str]) -> dict[str, Any]:
        """Get a nested object using a path (a list of keys)."""
        for key in paths:
            obj = obj.get(key, {})
        return obj
