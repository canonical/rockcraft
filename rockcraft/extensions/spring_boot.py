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

"""An extension for the Java runtime."""

import os
from typing import Tuple
from typing import Any
from typing import Dict
from overrides import override

from ..errors import ExtensionError
from .extension import Extension


class SpringBootFramework(Extension):

    def _check_project(self):
        """Ensure that either pom.xml or gradlew is present."""
        if "spring-boot-framework/install-app" not in self.yaml_data.get("parts", {}):
            if not os.path.exists(f"{self.project_root}/pom.xml") and not os.path.exists(
                f"{self.project_root}/gradlew"
            ):
                raise ExtensionError(
                    "missing pom.xml or gradlew file",
                    doc_slug="/reference/extensions/spring-boot-framework",
                    logpath_report=False,
                )

    @property
    def name(self) -> str:
        """Return the normalized name of the rockcraft project."""
        return self.yaml_data["name"].replace("-", "_").lower()

    @staticmethod
    @override
    def get_supported_bases() -> Tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@24.04", "ubuntu:24.04"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:
        """Check if the extension is in an experimental state."""
        return True

    @override
    def get_part_snippet(self) -> Dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}

    def get_root_snippet(self) -> Dict[str, Any]:
        self._check_project()
        return {}

    def get_runtime_deps_part(self) -> Dict[str, Any]:
        if "spring-boot-framework/runtime-deps" not in self.yaml_data.get("parts", {}):
            return {
                "plugin": "nil",
                "source": "https://github.com/vpa1977/chisel-releases",
                "source-type": "git",
                "source-branch": "24.04-openjdk-21-jre-headless",
                "override-build": """
                    chisel cut --release ./ --root ${CRAFT_PART_INSTALL} \
                        base-files_base \
                        libc6_libs \
                        libgcc-s1_libs \
                        libstdc++6_libs \
                        zlib1g_libs \
                        libnss3_libs
                    craftctl default
                """,
            }

    def gen_install_app_part(self) -> Dict[str, Any]:
        if "spring-boot-framework/install-app" not in self.yaml_data.get("parts", {}):
            if os.path.exists(f"{self.project_root}/pom.xml"):
                return {
                    "plugin": "nil",
                    "source": ".",
                    "source-type": "local",
                    "build-packages": ["openjdk-21-jdk", "maven"],
                    "build-environment": [
                        {
                            "JAVA_HOME": "/usr/lib/jvm/java-21-openjdk-${CRAFT_ARCH_BUILD_FOR}"
                        }
                    ],
                    "override-build": """
                        mvn package
                        mkdir -p ${CRAFT_PART_INSTALL}/jars
                        find ${CRAFT_PART_BUILD}/target -iname "*.jar" -exec ln {} ${CRAFT_PART_INSTALL}/jars \\;
                        craftctl default
                    """,
                }
            elif os.path.exists(f"{self.project_root}/gradlew"):
                return {
                    "plugin": "nil",
                    "source": ".",
                    "source-type": "local",
                    "build-packages": ["openjdk-21-jdk"],
                    "build-environment": [
                        {
                            "JAVA_HOME": "/usr/lib/jvm/java-21-openjdk-${CRAFT_ARCH_BUILD_FOR}"
                        }
                    ],
                    "override-build": "./gradlew jar --no-daemon",
                    "override-stage": """
                                    mkdir -p ${CRAFT_STAGE}/jars
                                    find ${CRAFT_PART_BUILD}/build -iname "*.jar" -exec ln {} ${CRAFT_STAGE}/jars \\;
                                    craftctl default
                                    """,
                    "override-prime": """
                                    cp -r ${CRAFT_STAGE}/jars ${CRAFT_PRIME}
                                    craftctl default
                                    """,
                }
        return {}

    def get_runtime_app_part(self) -> Dict[str, Any]:
        if "spring-boot-framework/runtime" not in self.yaml_data.get("parts", {}):
            return {
                "plugin": "jlink",
                "after": [
                    "spring-boot-framework/install-app",
                    "spring-boot-framework/runtime-deps",
                ],
            }
        return {}

    def get_parts_snippet(self) -> dict[str, Any]:
        """Return the parts to add to parts."""
        return {
            "spring-boot-framework/install-app": self.gen_install_app_part(),
            "spring-boot-framework/runtime": self.get_runtime_app_part(),
            "spring-boot-framework/runtime-deps": self.get_runtime_deps_part(),
        }
