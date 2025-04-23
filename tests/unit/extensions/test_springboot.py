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


@pytest.fixture
def use_gradle_init_script(tmp_path, request):
    gradle_init_script_path = tmp_path / "init.gradle"
    if not request.param:
        gradle_init_script_path.unlink(missing_ok=True)
        return gradle_init_script_path
    gradle_init_script_path.touch(exist_ok=True)
    return gradle_init_script_path


@pytest.mark.parametrize(
    (
        "use_pom_xml",
        "use_mvnw",
        "use_build_gradle",
        "use_gradlew",
        "use_gradle_init_script",
        "expected",
    ),
    [
        (
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
        ),
        (
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
        ),
        (
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
        ),
        (
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
        ),
        (
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
                    "spring-boot-framework/install-app": {
                        "plugin": "gradle",
                        "source": ".",
                        "gradle-task": "bootJar",
                        "gradle-init-script": "init.gradle",
                        "build-packages": ["default-jdk"],
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
        ),
    ],
    indirect=[
        "use_pom_xml",
        "use_mvnw",
        "use_build_gradle",
        "use_gradlew",
        "use_gradle_init_script",
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
    use_gradle_init_script,
    expected,
):
    applied = extensions.apply_extensions(tmp_path, spring_boot_input_yaml)
    # prefix init script from tmp_path
    if use_gradle_init_script.exists():
        expected["parts"]["spring-boot-framework/install-app"]["gradle-init-script"] = (
            str(
                tmp_path
                / expected["parts"]["spring-boot-framework/install-app"][
                    "gradle-init-script"
                ]
            )
        )

    assert applied == expected


@pytest.mark.parametrize(
    ("use_pom_xml", "use_mvnw", "use_build_gradle", "use_gradlew", "expected_err"),
    [
        (True, False, True, False, "both pom.xml and build.gradle files exist"),
        (False, True, False, True, "both mvnw and gradlew executable files exist"),
        (False, False, False, False, "missing pom.xml and build.gradle file"),
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
    ),
    [(True, False, True, False), (False, True, False, True)],
    indirect=True,
)
@pytest.mark.usefixtures("spring_boot_extension")
def test_spring_boot_extensions_check_project_non_executable_wrappers(
    tmp_path,
    spring_boot_input_yaml,
    use_mvnw_non_executable,
    use_gradlew_non_executable,
    use_pom_xml,
    use_build_gradle,
):
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, spring_boot_input_yaml)

    assert "mvnw or gradlew file is not executable" in str(exc.value)
