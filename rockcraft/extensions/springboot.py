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

"""An extension for the Java Spring Boot application."""

import os
import pathlib
from typing import Any, Literal

from overrides import override  # type: ignore[reportUnknownVariableType]

from rockcraft.errors import ExtensionError

from .extension import Extension


class SpringBootFramework(Extension):
    """An extension for constructing Java applications based on the Spring Boot framework."""

    @property
    def name(self) -> str:
        """Return the normalized name of the rockcraft project."""
        return self.yaml_data["name"].replace("-", "_").lower()

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

    def get_root_snippet(self) -> dict[str, Any]:
        """Return the root snippet to apply."""
        self._check_project()

        snippet: dict[str, Any] = {
            "run-user": "_daemon_",
            "services": {
                "spring-boot": {
                    "override": "replace",
                    "startup": "enabled",
                    "user": "_daemon_",
                    "working-dir": "/app",
                    "command": 'bash -c "java -jar *.jar"',
                }
            },
        }

        snippet["parts"] = {
            "spring-boot-framework/install-app": self.gen_install_app_part(),
            "spring-boot-framework/runtime": self.gen_runtime_app_part(),
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

    def _check_project(self) -> None:
        """Check if the project is a Spring Boot project."""
        if self.pom_xml_path.exists() and self.build_gradle_path.exists():
            raise ExtensionError(
                "both pom.xml and build.gradle files exist",
                doc_slug="/reference/extensions/spring-boot-framework",
                logpath_report=False,
            )
        if self.mvnw_path.exists() and self.gradlew_path.exists():
            raise ExtensionError(
                "both mvnw and gradlew executable files exist",
                doc_slug="/reference/extensions/spring-boot-framework",
                logpath_report=False,
            )
        if not self.pom_xml_path.exists() and not self.build_gradle_path.exists():
            raise ExtensionError(
                "missing pom.xml and build.gradle file",
                doc_slug="/reference/extensions/spring-boot-framework",
                logpath_report=False,
            )
        if (self.mvnw_path.exists() and not os.access(self.mvnw_path, os.X_OK)) or (
            self.gradlew_path.exists() and not os.access(self.gradlew_path, os.X_OK)
        ):
            raise ExtensionError(
                "mvnw or gradlew file is not executable",
                doc_slug="/reference/extensions/spring-boot-framework",
                logpath_report=False,
            )

    @property
    def mvnw_path(self) -> pathlib.Path:
        """Return the path to the mvnw file."""
        return self.project_root / "mvnw"

    @property
    def pom_xml_path(self) -> pathlib.Path:
        """Return the path to the pom.xml file."""
        return self.project_root / "pom.xml"

    @property
    def gradlew_path(self) -> pathlib.Path:
        """Return the path to the gradlew file."""
        return self.project_root / "gradlew"

    @property
    def build_gradle_path(self) -> pathlib.Path:
        """Return the path to the build.gradle file."""
        return self.project_root / "build.gradle"

    @property
    def init_gradle_path(self) -> pathlib.Path | None:
        """Return the path to the init.gradle file."""
        return next(
            (file for file in self.project_root.rglob("init.gradle") if file.is_file()),
            None,
        )

    @property
    def _rock_base(self) -> str:
        """Return the base of the rockcraft project."""
        return self.yaml_data["base"]

    def gen_install_app_part(self) -> dict[str, Any]:
        """Generate the install-app part."""
        if self.mvnw_path.exists() and self.gradlew_path.exists():
            raise ExtensionError(
                "Both mvnw and gradlew exist. Please remove one of them."
            )

        user_build_packages_override = (
            self.yaml_data.get("parts", {})
            .get("spring-boot-framework/install-app", {})
            .get("build-packages", [])
        )
        plugin: Literal["gradle", "maven"] = (
            "gradle" if self.build_gradle_path.exists() else "maven"
        )
        install_app_part = {
            "plugin": plugin,
            "source": ".",
            "build-packages": (
                user_build_packages_override
                if user_build_packages_override
                else self._gen_install_app_build_packages(plugin=plugin)
            ),
            "override-build": "craftctl default\n"
            "find ${CRAFT_PART_INSTALL} -name '*-plain.jar' -type f -delete",
            **self._gen_install_app_plugin_directives(plugin=plugin),
            "organize": {"**/*.jar": "app/"},
        }
        if self._rock_base == "bare":
            install_app_part["stage-packages"] = ["zlib1g", "libstdc++6"]
        return install_app_part

    def _gen_install_app_build_packages(
        self, plugin: Literal["gradle", "maven"]
    ) -> list[str]:
        """Generate build packages for corresponding plugin."""
        build_packages: list[str] = ["default-jdk"]
        if plugin == "gradle" and not self.gradlew_path.exists():
            build_packages.append("gradle")
        if plugin == "maven" and not self.mvnw_path.exists():
            build_packages.append("maven")
        return build_packages

    def _gen_install_app_plugin_directives(
        self, plugin: Literal["gradle", "maven"]
    ) -> dict[str, Any]:
        """Generate plugin specific directives."""
        plugin_directives: dict[str, Any] = {}
        if plugin == "gradle":
            plugin_directives["gradle-task"] = "bootJar"
        if plugin == "gradle" and self.init_gradle_path:
            plugin_directives["gradle-init-script"] = str(self.init_gradle_path)
        if plugin == "maven" and self.mvnw_path.exists():
            plugin_directives["maven-use-mvnw"] = "True"
        return plugin_directives

    def gen_runtime_app_part(self) -> dict[str, Any]:
        """Return the runtime part."""
        user_build_packages_override = (
            self.yaml_data.get("parts", {})
            .get("spring-boot-framework/runtime", {})
            .get("build-packages")
        )
        runtime_part = {
            "plugin": "jlink",
            "after": ["spring-boot-framework/install-app"],
            "build-packages": (
                user_build_packages_override
                if user_build_packages_override
                else ["default-jdk"]
            ),
        }
        if self._rock_base == "bare":
            runtime_part["stage-packages"] = [
                "bash_bins",
                "ca-certificates_data",
                "coreutils_bins",
                "base-files_tmp",
            ]

        return runtime_part
