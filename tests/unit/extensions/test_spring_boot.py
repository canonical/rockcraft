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
import textwrap

import pytest
from rockcraft import extensions
from rockcraft.errors import ExtensionError


@pytest.fixture(name="spring_boot_input_yaml")
def spring_boot_input_yaml_fixture():
    return {
        "name": "springboot",
        "base": "ubuntu@24.04",
        "platforms": {"amd64": {}},
        "extensions": ["spring-boot-framework"],
    }


@pytest.fixture
def spring_boot_extension(mock_extensions, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    extensions.register("spring-boot-framework", extensions.SpringBootFramework)


@pytest.mark.usefixtures("spring_boot_extension")
def test_spring_boot_extension_maven(tmp_path, spring_boot_input_yaml):
    (tmp_path / "pom.xml").write_text("<project/>")
    applied = extensions.apply_extensions(tmp_path, spring_boot_input_yaml)

    assert applied == {
        "base": "ubuntu@24.04",
        "name": "springboot",
        "platforms": {"amd64": {}},
        "run_user": "_daemon_",
        "parts": {
            "spring-boot-framework/install-app": {
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
            },
            "spring-boot-framework/runtime": {
                "plugin": "jlink",
                "after": [
                    "spring-boot-framework/install-app",
                    "spring-boot-framework/runtime-deps",
                ],
            },
            "spring-boot-framework/runtime-deps": {
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
            },
        },
    }


@pytest.mark.usefixtures("spring_boot_extension")
def test_spring_boot_extension_gradle(tmp_path, spring_boot_input_yaml):
    (tmp_path / "gradlew").write_text("<project/>")
    applied = extensions.apply_extensions(tmp_path, spring_boot_input_yaml)

    assert applied == {
        "base": "ubuntu@24.04",
        "name": "springboot",
        "platforms": {"amd64": {}},
        "run_user": "_daemon_",
        "parts": {
            "spring-boot-framework/install-app": {
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
            },
            "spring-boot-framework/runtime": {
                "plugin": "jlink",
                "after": [
                    "spring-boot-framework/install-app",
                    "spring-boot-framework/runtime-deps",
                ],
            },
            "spring-boot-framework/runtime-deps": {
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
            },
        },
    }


@pytest.mark.usefixtures("spring_boot_extension")
def test_spring_boot_extension_no_project_error(tmp_path, spring_boot_input_yaml):
    (tmp_path / "somefile").write_text("random text")
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, spring_boot_input_yaml)
    assert str(exc.value) == "missing pom.xml or gradlew file"
    assert str(exc.value.doc_slug) == "/reference/extensions/spring-boot-framework"
