# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2025 Canonical Ltd.
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
import re
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
            **self.gen_gradle_init_script_part(),
            "spring-boot-framework/install-app": self.gen_install_app_part(),
            "spring-boot-framework/runtime": self.gen_runtime_app_part(),
        }

        assets_part = self.gen_assets_part()
        if assets_part:
            snippet["parts"]["spring-boot-framework/assets"] = assets_part

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
                "both pom.xml and build.gradle files exist\n"
                "you cannot have both Maven and Gradle build files in the same project",
                doc_slug="/reference/extensions/spring-boot-framework/#project-requirements",
                logpath_report=False,
            )
        if self.mvnw_path.exists() and self.gradlew_path.exists():
            raise ExtensionError(
                "both mvnw and gradlew executable files exist\n"
                "you cannot have both Maven and Gradle executables in the same project",
                doc_slug="/reference/extensions/spring-boot-framework/#project-requirements",
                logpath_report=False,
            )
        if not self.pom_xml_path.exists() and not self.build_gradle_path.exists():
            raise ExtensionError(
                "missing pom.xml and build.gradle file\n"
                "you must have either a Maven pom.xml or a Gradle build.gradle file in your project",
                doc_slug="/reference/extensions/spring-boot-framework/#project-requirements",
                logpath_report=False,
            )
        if (self.mvnw_path.exists() and not os.access(self.mvnw_path, os.X_OK)) or (
            self.gradlew_path.exists() and not os.access(self.gradlew_path, os.X_OK)
        ):
            raise ExtensionError(
                "mvnw or gradlew file is not executable\n"
                "the mvnw or gradlew file must have executable permissions",
                doc_slug="/reference/extensions/spring-boot-framework/#project-requirements",
                logpath_report=False,
            )

        if (
            self.user_gradle_init_script_part_override_build_override
            and not self.build_gradle_path.exists()
        ):
            raise ExtensionError(
                "gradle init script part is enabled for non-gradle build",
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
    def _rock_base(self) -> str:
        """Return the base of the rockcraft project."""
        return self.yaml_data["base"]

    @property
    def user_gradle_init_script_part_override_build_override(self) -> str:
        """Return the user's override-build part for gradle-init-script part."""
        return (
            self.yaml_data.get("parts", {})
            .get("spring-boot-framework/gradle-init-script", {})
            .get("override-build", "")
        )

    def gen_gradle_init_script_part(self) -> dict[str, Any]:
        """Generate the gradle-init-script part if required."""
        if not self.user_gradle_init_script_part_override_build_override:
            return {}
        return {
            "spring-boot-framework/gradle-init-script": {
                "plugin": "nil",
                "source": ".",
                "override-build": self.user_gradle_init_script_part_override_build_override,
                "prime": [],
            }
        }

    def gen_install_app_part(self) -> dict[str, Any]:
        """Generate the install-app part."""
        plugin: Literal["gradle", "maven"] = (
            "gradle" if self.build_gradle_path.exists() else "maven"
        )
        install_app_part = {
            "source": ".",
            "organize": {
                "**/*.jar": "app/",
            },
            **(
                self._gen_install_app_gradle_plugin()
                if plugin == "gradle"
                else self._gen_install_app_maven_plugin()
            ),
        }

        if self._rock_base == "bare":
            install_app_part["stage-packages"] = [
                "libnss3_nss",
                "libc6_libs",
                "libgcc-s1_libs",
                "libstdc++6_libs",
                "zlib1g_libs",
            ]
        return install_app_part

    @property
    def _user_install_app_build_packages_override(self) -> list[str]:
        return (
            self.yaml_data.get("parts", {})
            .get("spring-boot-framework/install-app", {})
            .get("build-packages", [])
        )

    DEFAULT_BUILD_PACKAGES = ["default-jdk"]
    DEFAULT_OVERRIDE_BUILD_COMMANDS = [
        "craftctl default",
        "find ${CRAFT_PART_INSTALL} -name '*-plain.jar' -type f -delete",
    ]
    # The Gradle plugin's JavaPlugin base class hardlinks ALL JARs found under
    # ${CRAFT_PART_BUILD} (including Gradle's own distribution and cache JARs
    # from .gradle/wrapper/dists/ and .gradle/caches/) into
    # ${CRAFT_PART_INSTALL}/jar/.  Those extra JARs then get staged alongside
    # the Spring Boot fat JAR and cause `jdeps` (used by the jlink plugin) to
    # fail with a FindException: some of Gradle's own JARs are named modules
    # (e.g. log4j-to-slf4j) that require automatic modules (e.g. org.slf4j)
    # whose provider JAR (slf4j-api-1.7.x, bundled by Gradle) lacks the
    # Automatic-Module-Name manifest entry.  --ignore-missing-deps does not
    # suppress this error because it occurs during jdeps' module-graph
    # construction phase, before analysis begins.
    #
    # The fix: after craftctl default, identify the Spring Boot fat JAR by
    # looking in build/libs/ (where bootJar always places its output) and
    # delete every other JAR from the install directory.  The fat JAR name is
    # discovered at build time via shell commands, so no prior knowledge of the
    # artifact name is required.
    GRADLE_OVERRIDE_BUILD_COMMANDS = [
        *DEFAULT_OVERRIDE_BUILD_COMMANDS,
        "SPRING_FAT_JAR=$(find ${CRAFT_PART_BUILD}/build/libs"
        " -name '*.jar' ! -name '*-plain.jar' -type f -printf '%f\\n' | head -1)",
        'find ${CRAFT_PART_INSTALL}/jar -name "*.jar" ! -name "${SPRING_FAT_JAR}" -delete',
    ]

    def _gen_install_app_gradle_plugin(self) -> dict[str, Any]:
        """Generate install app part using Gradle plugin."""
        gradle_install_app_part: dict[str, Any] = {
            "plugin": "gradle",
            "gradle-task": "bootJar",
        }

        build_packages = [*self.DEFAULT_BUILD_PACKAGES]
        if not self.gradlew_path.exists():
            build_packages += ["gradle"]
        gradle_install_app_part["build-packages"] = build_packages

        override_build_cmds: list[str] = []
        if self.yaml_data.get("parts", {}).get(
            "spring-boot-framework/gradle-init-script", {}
        ):
            gradle_install_app_part["build-environment"] = [
                {"GRADLE_USER_HOME": "${CRAFT_PART_BUILD}/.gradle/"}
            ]
            gradle_install_app_part["after"] = [
                "spring-boot-framework/gradle-init-script"
            ]
            override_build_cmds += [
                "mkdir -p ${CRAFT_PART_BUILD}/.gradle/",
                "cp ${CRAFT_STAGE}/*init.gradle* ${CRAFT_PART_BUILD}/.gradle/",
            ]
        override_build_cmds += self.GRADLE_OVERRIDE_BUILD_COMMANDS
        gradle_install_app_part["override-build"] = "\n".join(override_build_cmds)
        return gradle_install_app_part

    def _gen_install_app_maven_plugin(self) -> dict[str, Any]:
        """Generate install app part using maven plugin."""
        build_packages = [*self.DEFAULT_BUILD_PACKAGES]
        if not self.mvnw_path.exists():
            build_packages += ["maven"]
        maven_install_app = {
            "plugin": "maven",
            "build-packages": self._user_install_app_build_packages_override
            or build_packages,
            "override-build": "\n".join(self.DEFAULT_OVERRIDE_BUILD_COMMANDS),
        }
        if self.mvnw_path.exists():
            maven_install_app["maven-use-wrapper"] = "True"
        return maven_install_app

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
                "base-files_chisel",
                "base-files_tmp",
                "coreutils_bins",
            ]

        return runtime_part

    def gen_assets_part(self) -> dict[str, Any] | None:
        """Generate assets-stage part for extra assets in the project."""
        # if stage is not in exclude mode, use it to generate organize
        assets_stage = self._get_assets_stage()

        if assets_stage and assets_stage[0] and assets_stage[0][0] != "-":
            renaming_map = {os.path.relpath(file, "app"): file for file in assets_stage}
        else:
            return None

        return {
            "plugin": "dump",
            "source": ".",
            "organize": renaming_map,
            "stage": assets_stage,
        }

    def _get_assets_stage(self) -> list[str]:
        """Return the assets stage list for the Spring Boot project."""
        user_stage = (
            self.yaml_data.get("parts", {})
            .get("spring-boot-framework/assets", {})
            .get("stage", [])
        )

        if not all(re.match("-? *app/", p) for p in user_stage):
            raise ExtensionError(
                "The spring-boot-framework extension requires the 'stage' entry in the "
                "spring-boot-framework/assets part to start with 'app/'",
                doc_slug="/reference/extensions/spring-boot-framework",
                logpath_report=False,
            )
        if not user_stage:
            user_stage = [
                f"app/{f}"
                for f in (
                    "migrate",
                    "migrate.sh",
                )
                if (self.project_root / f).exists()
            ]
        return user_stage
