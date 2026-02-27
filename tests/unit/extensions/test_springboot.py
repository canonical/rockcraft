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


import pytest
from rockcraft import extensions
from rockcraft.errors import ExtensionError


@pytest.fixture(name="spring_boot_input_yaml")
def spring_boot_input_yaml_fixture():
    return {
        "name": "springbootprojectname",
        "base": "ubuntu@24.04",
        "platforms": {"amd64": {}},
        "extensions": ["spring-boot-framework"],
    }


@pytest.fixture(name="use_gradle_init_script_part")
def use_gradle_init_script_part_fixture(request, spring_boot_input_yaml):
    if not request.param:
        return
    gradle_init_script_part = {
        "spring-boot-framework/gradle-init-script": {
            "override-build": "cp *init.gradle* ${CRAFT_STAGE}/"
        }
    }
    spring_boot_input_yaml["parts"] = gradle_init_script_part
    return


@pytest.fixture
def spring_boot_extension(mock_extensions, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    extensions.register("spring-boot-framework", extensions.SpringBootFramework)


@pytest.fixture
def use_pom_xml(tmp_path, request):
    pom_xml_path = tmp_path / "pom.xml"
    if not request.param:
        pom_xml_path.unlink(missing_ok=True)
        return
    pom_xml_path.touch(exist_ok=True)
    return


@pytest.fixture
def use_mvnw(tmp_path, request):
    mvnw_path = tmp_path / "mvnw"
    if not request.param:
        mvnw_path.unlink(missing_ok=True)
        return
    mvnw_path.touch(exist_ok=True)
    mvnw_path.chmod(0o777)


@pytest.fixture
def use_mvnw_non_executable(tmp_path, request):
    if not request.param:
        return
    (tmp_path / "mvnw").touch()


@pytest.fixture
def use_build_gradle(tmp_path, request):
    build_gradle_path = tmp_path / "build.gradle"
    if not request.param:
        build_gradle_path.unlink(missing_ok=True)
        return
    build_gradle_path.touch(exist_ok=True)
    return


@pytest.fixture
def use_gradlew(tmp_path, request):
    gradlew_path = tmp_path / "gradlew"
    if not request.param:
        gradlew_path.unlink(missing_ok=True)
        return
    gradlew_path.touch(exist_ok=True)
    gradlew_path.chmod(0o777)


@pytest.fixture
def use_gradlew_non_executable(tmp_path, request):
    if not request.param:
        return
    (tmp_path / "gradlew").touch()


@pytest.mark.parametrize(
    (
        "use_pom_xml",
        "use_mvnw",
        "use_build_gradle",
        "use_gradlew",
        "use_gradle_init_script_part",
        "expected",
    ),
    [
        pytest.param(
            True,
            False,
            False,
            False,
            False,
            {
                "base": "ubuntu@24.04",
                "name": "springbootprojectname",
                "platforms": {"amd64": {}},
                "run-user": "_daemon_",
                "parts": {
                    "spring-boot-framework/install-app": {
                        "plugin": "maven",
                        "source": ".",
                        "build-packages": [
                            "default-jdk",
                            "maven",
                        ],
                        "organize": {
                            "**/*.jar": "app/",
                        },
                        "override-build": "craftctl default\n"
                        "find ${CRAFT_PART_INSTALL} -name '*-plain.jar' -type f -delete",
                    },
                    "spring-boot-framework/runtime": {
                        "plugin": "jlink",
                        "after": ["spring-boot-framework/install-app"],
                        "build-packages": ["default-jdk"],
                    },
                },
                "services": {
                    "spring-boot": {
                        "command": 'bash -c "java -jar *.jar"',
                        "override": "replace",
                        "startup": "enabled",
                        "user": "_daemon_",
                        "working-dir": "/app",
                    }
                },
            },
            id="use maven from archive (mvnw file not present)",
        ),
        pytest.param(
            True,
            True,
            False,
            False,
            False,
            {
                "base": "ubuntu@24.04",
                "name": "springbootprojectname",
                "platforms": {"amd64": {}},
                "run-user": "_daemon_",
                "parts": {
                    "spring-boot-framework/install-app": {
                        "plugin": "maven",
                        "source": ".",
                        "build-packages": ["default-jdk"],
                        "maven-use-wrapper": "True",
                        "organize": {
                            "**/*.jar": "app/",
                        },
                        "override-build": "craftctl default\n"
                        "find ${CRAFT_PART_INSTALL} -name '*-plain.jar' -type f -delete",
                    },
                    "spring-boot-framework/runtime": {
                        "plugin": "jlink",
                        "after": ["spring-boot-framework/install-app"],
                        "build-packages": ["default-jdk"],
                    },
                },
                "services": {
                    "spring-boot": {
                        "command": 'bash -c "java -jar *.jar"',
                        "override": "replace",
                        "startup": "enabled",
                        "user": "_daemon_",
                        "working-dir": "/app",
                    }
                },
            },
            id="use maven wrapper (mvnw file present)",
        ),
        pytest.param(
            False,
            False,
            True,
            False,
            False,
            {
                "base": "ubuntu@24.04",
                "name": "springbootprojectname",
                "platforms": {"amd64": {}},
                "run-user": "_daemon_",
                "parts": {
                    "spring-boot-framework/install-app": {
                        "plugin": "gradle",
                        "source": ".",
                        "gradle-task": "bootJar",
                        "build-packages": [
                            "default-jdk",
                            "gradle",
                        ],
                        "organize": {
                            "**/*.jar": "app/",
                        },
                        "override-build": (
                            "craftctl default\n"
                            "find ${CRAFT_PART_INSTALL} -name '*-plain.jar' -type f -delete\n"
                            "SPRING_FAT_JAR=$(find ${CRAFT_PART_BUILD}/build/libs"
                            " -name '*.jar' ! -name '*-plain.jar' -type f -printf '%f\\n' | head -1)\n"
                            'find ${CRAFT_PART_INSTALL}/jar -name "*.jar" ! -name "${SPRING_FAT_JAR}" -delete'
                        ),
                    },
                    "spring-boot-framework/runtime": {
                        "plugin": "jlink",
                        "after": ["spring-boot-framework/install-app"],
                        "build-packages": ["default-jdk"],
                    },
                },
                "services": {
                    "spring-boot": {
                        "command": 'bash -c "java -jar *.jar"',
                        "override": "replace",
                        "startup": "enabled",
                        "user": "_daemon_",
                        "working-dir": "/app",
                    }
                },
            },
            id="use gradle from archive (gradlew file not present)",
        ),
        pytest.param(
            False,
            False,
            True,
            True,
            False,
            {
                "base": "ubuntu@24.04",
                "name": "springbootprojectname",
                "platforms": {"amd64": {}},
                "run-user": "_daemon_",
                "parts": {
                    "spring-boot-framework/install-app": {
                        "plugin": "gradle",
                        "source": ".",
                        "gradle-task": "bootJar",
                        "build-packages": ["default-jdk"],
                        "organize": {
                            "**/*.jar": "app/",
                        },
                        "override-build": (
                            "craftctl default\n"
                            "find ${CRAFT_PART_INSTALL} -name '*-plain.jar' -type f -delete\n"
                            "SPRING_FAT_JAR=$(find ${CRAFT_PART_BUILD}/build/libs"
                            " -name '*.jar' ! -name '*-plain.jar' -type f -printf '%f\\n' | head -1)\n"
                            'find ${CRAFT_PART_INSTALL}/jar -name "*.jar" ! -name "${SPRING_FAT_JAR}" -delete'
                        ),
                    },
                    "spring-boot-framework/runtime": {
                        "plugin": "jlink",
                        "after": ["spring-boot-framework/install-app"],
                        "build-packages": ["default-jdk"],
                    },
                },
                "services": {
                    "spring-boot": {
                        "command": 'bash -c "java -jar *.jar"',
                        "override": "replace",
                        "startup": "enabled",
                        "user": "_daemon_",
                        "working-dir": "/app",
                    }
                },
            },
            id="use gradlew (gradlew file present)",
        ),
        pytest.param(
            False,
            False,
            True,
            True,
            True,
            {
                "base": "ubuntu@24.04",
                "name": "springbootprojectname",
                "platforms": {"amd64": {}},
                "run-user": "_daemon_",
                "parts": {
                    "spring-boot-framework/gradle-init-script": {
                        "override-build": "cp *init.gradle* ${CRAFT_STAGE}/",
                        "plugin": "nil",
                        "source": ".",
                        "prime": [],
                    },
                    "spring-boot-framework/install-app": {
                        "after": [
                            "spring-boot-framework/gradle-init-script",
                        ],
                        "plugin": "gradle",
                        "source": ".",
                        "gradle-task": "bootJar",
                        "build-packages": ["default-jdk"],
                        "build-environment": [
                            {
                                "GRADLE_USER_HOME": "${CRAFT_PART_BUILD}/.gradle/",
                            },
                        ],
                        "organize": {
                            "**/*.jar": "app/",
                        },
                        "override-build": (
                            "mkdir -p ${CRAFT_PART_BUILD}/.gradle/\n"
                            "cp ${CRAFT_STAGE}/*init.gradle* ${CRAFT_PART_BUILD}/.gradle/\n"
                            "craftctl default\n"
                            "find ${CRAFT_PART_INSTALL} -name '*-plain.jar' -type f -delete\n"
                            "SPRING_FAT_JAR=$(find ${CRAFT_PART_BUILD}/build/libs"
                            " -name '*.jar' ! -name '*-plain.jar' -type f -printf '%f\\n' | head -1)\n"
                            'find ${CRAFT_PART_INSTALL}/jar -name "*.jar" ! -name "${SPRING_FAT_JAR}" -delete'
                        ),
                    },
                    "spring-boot-framework/runtime": {
                        "plugin": "jlink",
                        "after": ["spring-boot-framework/install-app"],
                        "build-packages": ["default-jdk"],
                    },
                },
                "services": {
                    "spring-boot": {
                        "command": 'bash -c "java -jar *.jar"',
                        "override": "replace",
                        "startup": "enabled",
                        "user": "_daemon_",
                        "working-dir": "/app",
                    }
                },
            },
            id="use gradle init script",
        ),
    ],
    indirect=[
        "use_pom_xml",
        "use_mvnw",
        "use_build_gradle",
        "use_gradlew",
        "use_gradle_init_script_part",
    ],
)
@pytest.mark.usefixtures("spring_boot_extension")
def test_spring_boot_extension_default(
    tmp_path,
    spring_boot_input_yaml,
    use_pom_xml,
    use_mvnw,
    use_build_gradle,
    use_gradlew,
    use_gradle_init_script_part,
    expected,
):
    applied = extensions.apply_extensions(tmp_path, spring_boot_input_yaml)

    assert applied == expected


@pytest.mark.parametrize(
    ("use_pom_xml", "use_mvnw", "use_build_gradle", "use_gradlew", "expected_err"),
    [
        pytest.param(
            True,
            False,
            True,
            False,
            "both pom.xml and build.gradle files exist",
            id="unable to determine plugin",
        ),
        pytest.param(
            False,
            True,
            False,
            True,
            "both mvnw and gradlew executable files exist",
            id="both wrappers present",
        ),
        pytest.param(
            False,
            False,
            False,
            False,
            "missing pom.xml and build.gradle file",
            id="no build system detected",
        ),
    ],
    indirect=[
        "use_pom_xml",
        "use_mvnw",
        "use_build_gradle",
        "use_gradlew",
    ],
)
@pytest.mark.usefixtures("spring_boot_extension")
def test_spring_boot_extension_check_project(
    tmp_path,
    spring_boot_input_yaml,
    use_pom_xml,
    use_mvnw,
    use_build_gradle,
    use_gradlew,
    expected_err,
):
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, spring_boot_input_yaml)

    assert expected_err in str(exc.value)


@pytest.mark.parametrize(
    (
        "use_mvnw_non_executable",
        "use_gradlew_non_executable",
        "use_pom_xml",
        "use_build_gradle",
        "use_gradle_init_script_part",
        "expected_error",
    ),
    [
        pytest.param(
            False,
            False,
            True,
            True,
            False,
            "both pom.xml and build.gradle files exist",
            id="multiple build system detected",
        ),
        pytest.param(
            True,
            True,
            True,
            False,
            False,
            "both mvnw and gradlew executable files exist",
            id="multiple build system wrappers detected",
        ),
        pytest.param(
            False,
            False,
            False,
            False,
            False,
            "missing pom.xml and build.gradle file",
            id="no build system detected",
        ),
        pytest.param(
            False,
            True,
            False,
            True,
            False,
            "mvnw or gradlew file is not executable",
            id="non executable build system wrappers",
        ),
        pytest.param(
            False,
            False,
            True,
            False,
            True,
            "gradle init script part is enabled for non-gradle build",
            id="gradle init script part defined for maven project",
        ),
    ],
    indirect=[
        "use_mvnw_non_executable",
        "use_gradlew_non_executable",
        "use_pom_xml",
        "use_build_gradle",
        "use_gradle_init_script_part",
    ],
)
@pytest.mark.usefixtures("spring_boot_extension")
def test_spring_boot_extensions_check_project_errors(
    tmp_path,
    spring_boot_input_yaml,
    use_mvnw_non_executable,
    use_gradlew_non_executable,
    use_pom_xml,
    use_build_gradle,
    use_gradle_init_script_part,
    expected_error,
):
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, spring_boot_input_yaml)

    assert expected_error in str(exc.value)


@pytest.mark.usefixtures("spring_boot_extension")
def test_spring_boot_extension_extra_assets(tmp_path, spring_boot_input_yaml):
    (tmp_path / "pom.xml").touch(exist_ok=True)
    (tmp_path / "migrate").write_text("migrate")
    (tmp_path / "migrate.sh").write_text("migrate")
    (tmp_path / "test").write_text("test")
    applied = extensions.apply_extensions(tmp_path, spring_boot_input_yaml)
    assert applied["parts"]["spring-boot-framework/assets"] == {
        "plugin": "dump",
        "source": ".",
        "organize": {
            "migrate": "app/migrate",
            "migrate.sh": "app/migrate.sh",
        },
        "stage": ["app/migrate", "app/migrate.sh"],
    }


@pytest.mark.usefixtures("spring_boot_extension")
def test_spring_boot_extension_extra_assets_overridden(
    tmp_path, spring_boot_input_yaml
):
    (tmp_path / "pom.xml").touch(exist_ok=True)
    (tmp_path / "migrate").write_text("migrate")
    (tmp_path / "migrate.sh").write_text("migrate")
    spring_boot_input_yaml["parts"] = {
        "spring-boot-framework/assets": {
            "plugin": "dump",
            "source": ".",
            "stage": ["app/foobar"],
        }
    }
    applied = extensions.apply_extensions(tmp_path, spring_boot_input_yaml)
    assert applied["parts"]["spring-boot-framework/assets"] == {
        "plugin": "dump",
        "source": ".",
        "organize": {
            "foobar": "app/foobar",
        },
        "stage": ["app/foobar"],
    }


@pytest.mark.usefixtures("spring_boot_extension")
def test_spring_boot_extension_extra_assets_start_with_app(
    tmp_path, spring_boot_input_yaml
):
    (tmp_path / "pom.xml").touch(exist_ok=True)
    (tmp_path / "migrate").write_text("migrate")
    (tmp_path / "migrate.sh").write_text("migrate")
    spring_boot_input_yaml["parts"] = {
        "spring-boot-framework/assets": {
            "plugin": "dump",
            "source": ".",
            "stage": ["foobar_not_in_app"],
        }
    }
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, spring_boot_input_yaml)

    assert "start with 'app/'" in str(exc.value)
