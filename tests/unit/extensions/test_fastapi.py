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
import pytest
from rockcraft import extensions
from rockcraft.errors import ExtensionError


@pytest.fixture(name="fastapi_input_yaml")
def fastapi_input_yaml_fixture():
    return {
        "name": "foo-bar",
        "base": "ubuntu@24.04",
        "platforms": {"amd64": {}},
        "extensions": ["fastapi-framework"],
    }


@pytest.fixture
def fastapi_extension(mock_extensions):
    extensions.register("fastapi-framework", extensions.fastapi_framework_factory)  # type: ignore[arg-type]


@pytest.mark.usefixtures("fastapi_extension")
@pytest.mark.parametrize(
    "packages", ["other\nfastapi", "fastapi", "Fastapi", " fastapi == 99", "starlette"]
)
def test_fastapi_extension_default(tmp_path, fastapi_input_yaml, packages):
    (tmp_path / "requirements.txt").write_text(packages)
    (tmp_path / "app.py").write_text("app = object()")
    applied = extensions.apply_extensions(tmp_path, fastapi_input_yaml)

    assert applied == {
        "base": "ubuntu@24.04",
        "name": "foo-bar",
        "platforms": {"amd64": {}},
        "run_user": "_daemon_",
        "parts": {
            "fastapi-framework/dependencies": {
                "build-environment": [],
                "plugin": "python",
                "stage-packages": ["python3-venv"],
                "source": ".",
                "python-packages": ["uvicorn"],
                "python-requirements": ["requirements.txt"],
            },
            "fastapi-framework/install-app": {
                "plugin": "dump",
                "source": ".",
                "organize": {
                    "app.py": "app/app.py",
                },
                "stage": ["app/app.py"],
                "permissions": [{"owner": 584792, "group": 584792}],
            },
            "fastapi-framework/runtime": {
                "plugin": "nil",
                "stage-packages": ["ca-certificates_data"],
            },
            "fastapi-framework/logging": {
                "plugin": "nil",
                "override-build": (
                    "craftctl default\n"
                    "mkdir -p $CRAFT_PART_INSTALL/opt/promtail\n"
                    "mkdir -p $CRAFT_PART_INSTALL/etc/promtail"
                ),
                "permissions": [
                    {"path": "opt/promtail", "owner": 584792, "group": 584792},
                    {"path": "etc/promtail", "owner": 584792, "group": 584792},
                ],
            },
        },
        "services": {
            "fastapi": {
                "command": "/bin/python3 -m uvicorn app:app",
                "override": "replace",
                "startup": "enabled",
                "user": "_daemon_",
                "working-dir": "/app",
                "environment": {
                    "UVICORN_HOST": "0.0.0.0",  # noqa: S104
                },
            },
        },
    }


@pytest.mark.parametrize(
    ("files", "organize", "command"),
    [
        (
            {"app.py": "app = object()"},
            {"app.py": "app/app.py"},
            "/bin/python3 -m uvicorn app:app",
        ),
        (
            {"app/__init__.py": "app = object()"},
            {"app": "app/app"},
            "/bin/python3 -m uvicorn app:app",
        ),
        (
            {"app/__init__.py": "from .app import app"},
            {"app": "app/app"},
            "/bin/python3 -m uvicorn app:app",
        ),
        (
            {"app/app.py": "app = object()"},
            {"app": "app/app"},
            "/bin/python3 -m uvicorn app.app:app",
        ),
        (
            {"app/main.py": "app = object()"},
            {"app": "app/app"},
            "/bin/python3 -m uvicorn app.main:app",
        ),
        (
            {"app/app.py": "app = object()", "app/__init__.py": "from .app import app"},
            {"app": "app/app"},
            "/bin/python3 -m uvicorn app:app",
        ),
        (
            {"src/app.py": "app = object()"},
            {"src": "app/src"},
            "/bin/python3 -m uvicorn src.app:app",
        ),
        (
            {"foo_bar/app.py": "app = object()"},
            {"foo_bar": "app/foo_bar"},
            "/bin/python3 -m uvicorn foo_bar.app:app",
        ),
        (
            {"app.py": "app = object()", "foo_bar/app.py": "app = object()"},
            {"app.py": "app/app.py"},
            "/bin/python3 -m uvicorn app:app",
        ),
    ],
)
@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_extension_asgi_entrypoints(
    tmp_path, fastapi_input_yaml, files, organize, command
):
    (tmp_path / "requirements.txt").write_text("fastapi")
    for file_path, content in files.items():
        (tmp_path / file_path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / file_path).write_text(content)
    applied = extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    install_app_part = applied["parts"]["fastapi-framework/install-app"]
    assert install_app_part["organize"] == organize
    assert applied["parts"]["fastapi-framework/install-app"]["stage"] == list(
        install_app_part["organize"].values()
    )
    assert applied["services"]["fastapi"]["command"] == command
    assert install_app_part["permissions"] == [{"owner": 584792, "group": 584792}]


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_wrong_asgi_entrypoint(tmp_path, fastapi_input_yaml):
    (tmp_path / "requirements.txt").write_text("fastapi")
    (tmp_path / "app.py").write_text("app = ")
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    assert "- Syntax error in  python file in ASGI search path" in str(exc.value)
    assert "invalid syntax (app.py, line 1)" in str(exc.value)


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_no_asgi_entrypoint(tmp_path, fastapi_input_yaml):
    (tmp_path / "requirements.txt").write_text("fastapi")
    (tmp_path / "app.py").write_text("a = b\n")
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    assert "- missing ASGI entrypoint" in str(exc.value)


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_missing_asgi_entrypoint(tmp_path, fastapi_input_yaml):
    (tmp_path / "requirements.txt").write_text("fastapi")
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    assert "- missing ASGI entrypoint" in str(exc.value)


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_missing_requirements_txt(tmp_path, fastapi_input_yaml):
    (tmp_path / "app.py").write_text("app = app")
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    assert str(exc.value) == (
        "- missing a requirements.txt file. The fastapi-framework extension requires this file with 'fastapi'/'starlette' specified as a dependency."
    )


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_check_no_correct_requirement_and_no_asgi_entrypoint(
    tmp_path, fastapi_input_yaml
):
    (tmp_path / "requirements.txt").write_text("oneproject")
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    assert str(exc.value) == (
        "- missing fastapi or starlette package dependency in requirements.txt file.\n"
        "- missing ASGI entrypoint\n"
        "  Cannot find 'app' global variable in the following places:\n"
        "  1. app.py.\n"
        "  2. In files __init__.py, and main.py in the 'app','src', "
        "and root project directories."
    )


@pytest.mark.parametrize(
    ("build_base", "expected_stage_packages", "expected_python_interpreter"),
    [
        ("ubuntu@24.04", ["python3.12-venv_ensurepip"], "python3.12"),
        ("ubuntu:24.04", ["python3.12-venv_ensurepip"], "python3.12"),
    ],
)
@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_extension_bare(
    tmp_path, build_base, expected_stage_packages, expected_python_interpreter
):
    (tmp_path / "requirements.txt").write_text("fastapi")
    (tmp_path / "app.py").write_text("app = object()")
    fastapi_input_yaml = {
        "name": "foo-bar",
        "extensions": ["fastapi-framework"],
        "base": "bare",
        "build-base": build_base,
        "platforms": {"amd64": {}},
    }
    applied = extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    assert applied["parts"]["fastapi-framework/dependencies"] == {
        "plugin": "python",
        "stage-packages": expected_stage_packages,
        "source": ".",
        "python-packages": ["uvicorn"],
        "python-requirements": ["requirements.txt"],
        "build-environment": [
            {"PARTS_PYTHON_INTERPRETER": expected_python_interpreter}
        ],
    }
    assert applied["parts"]["fastapi-framework/runtime"] == {
        "plugin": "nil",
        "override-build": "mkdir -m 777 ${CRAFT_PART_INSTALL}/tmp\n"
        "ln -sf /usr/bin/bash ${CRAFT_PART_INSTALL}/usr/bin/sh",
        "stage-packages": ["bash_bins", "coreutils_bins", "ca-certificates_data"],
    }


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_framework_exclude_prime(tmp_path, fastapi_input_yaml):
    (tmp_path / "requirements.txt").write_text("fastapi")
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "static").mkdir()
    (tmp_path / "webapp").mkdir()
    (tmp_path / "test").mkdir()
    (tmp_path / "node_modules").mkdir()
    fastapi_input_yaml["parts"] = {
        "fastapi-framework/install-app": {
            "prime": [
                "- app/app/test",
            ]
        }
    }
    applied = extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    install_app_part = applied["parts"]["fastapi-framework/install-app"]
    assert install_app_part["prime"] == ["- app/app/test"]
    assert install_app_part["organize"] == {
        "app.py": "app/app.py",
        "requirements.txt": "app/requirements.txt",
        "static": "app/static",
        "test": "app/test",
        "webapp": "app/webapp",
    }
    assert install_app_part["stage"] == [
        "app/app.py",
        "app/requirements.txt",
        "app/static",
        "app/test",
        "app/webapp",
    ]
    assert install_app_part["permissions"] == [{"owner": 584792, "group": 584792}]


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_framework_service_overridden(tmp_path, fastapi_input_yaml):
    (tmp_path / "requirements.txt").write_text("fastapi")
    (tmp_path / "webapp.py").write_text("app = object()")
    fastapi_input_yaml["services"] = {
        "fastapi": {"command": "/bin/python3 -m uvicorn webapp:app"}
    }
    applied = extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    assert (
        applied["services"]["fastapi"]["command"]
        == "/bin/python3 -m uvicorn webapp:app"
    )
    # As there is not file/directory to copy, the extension copies everything.
    assert applied["parts"]["fastapi-framework/install-app"] == {
        "plugin": "dump",
        "source": ".",
        "organize": {
            "requirements.txt": "app/requirements.txt",
            "webapp.py": "app/webapp.py",
        },
        "stage": ["app/requirements.txt", "app/webapp.py"],
        "permissions": [{"owner": 584792, "group": 584792}],
    }


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_extension_incorrect_prime_prefix_error(tmp_path, fastapi_input_yaml):
    (tmp_path / "requirements.txt").write_text("fastapi")
    (tmp_path / "app.py").write_text("app = object()")

    fastapi_input_yaml["parts"] = {
        "fastapi-framework/install-app": {"prime": ["app.py"]}
    }

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    assert "start with app/" in str(exc)
    assert "start with app/" in str(exc)


def test_factory_dispatch_v1(tmp_path):
    """Factory returns FastAPIFramework (V1) for ubuntu@24.04."""
    instance = extensions.fastapi_framework_factory(
        project_root=tmp_path, yaml_data={"name": "x", "base": "ubuntu@24.04"}
    )
    assert isinstance(instance, extensions.FastAPIFramework)
    assert not isinstance(instance, extensions.FastAPIFrameworkV2)


def test_factory_dispatch_v2(tmp_path):
    """Factory returns FastAPIFrameworkV2 for ubuntu@26.04."""
    instance = extensions.fastapi_framework_factory(
        project_root=tmp_path, yaml_data={"name": "x", "base": "ubuntu@26.04"}
    )
    assert isinstance(instance, extensions.FastAPIFrameworkV2)


def test_v2_supported_bases():
    """FastAPIFrameworkV2 supports ubuntu@26.04."""
    assert "ubuntu@26.04" in extensions.FastAPIFrameworkV2.get_supported_bases()


def test_factory_supported_bases():
    """fastapi_framework_factory includes both V1 and V2 bases."""
    factory_bases = extensions.fastapi_framework_factory.get_supported_bases()
    assert "ubuntu@26.04" in factory_bases
    for base in extensions.FastAPIFramework.get_supported_bases():
        assert base in factory_bases


def test_fastapi_framework_factory_is_experimental():
    factory = extensions.fastapi_framework_factory
    assert factory.is_experimental("ubuntu@26.04") is True
    assert factory.is_experimental("ubuntu@24.04") is False
    assert factory.is_experimental("bare") is False


def test_v2_is_experimental():
    """FastAPIFrameworkV2 is experimental."""
    assert extensions.FastAPIFrameworkV2.is_experimental("ubuntu@26.04") is True


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_extension_26_04_experimental_no_env(tmp_path):
    """Test that V2 extension requires experimental env var."""
    (tmp_path / "requirements.txt").write_text("fastapi")
    (tmp_path / "app.py").write_text("app = object()")
    input_yaml = {
        "name": "foo-bar",
        "base": "ubuntu@26.04",
        "platforms": {"amd64": {}},
        "extensions": ["fastapi-framework"],
    }
    with pytest.raises(ExtensionError, match="Extension is experimental"):
        extensions.apply_extensions(tmp_path, input_yaml)


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_extension_default_26_04(tmp_path, monkeypatch):
    """Full apply on ubuntu@26.04 yields the same output as 24.04 but with a 26.04 base."""
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    (tmp_path / "requirements.txt").write_text("fastapi")
    (tmp_path / "app.py").write_text("app = object()")
    input_yaml = {
        "name": "foo-bar",
        "base": "ubuntu@26.04",
        "platforms": {"amd64": {}},
        "extensions": ["fastapi-framework"],
    }
    applied = extensions.apply_extensions(tmp_path, input_yaml)

    assert applied == {
        "base": "ubuntu@26.04",
        "name": "foo-bar",
        "platforms": {"amd64": {}},
        "run_user": "_daemon_",
        "parts": {
            "fastapi-framework/dependencies": {
                "build-environment": [],
                "plugin": "python",
                "stage-packages": ["python3-venv"],
                "source": ".",
                "python-packages": ["uvicorn"],
                "python-requirements": ["requirements.txt"],
            },
            "fastapi-framework/install-app": {
                "plugin": "dump",
                "source": ".",
                "organize": {
                    "app.py": "app/app.py",
                },
                "stage": ["app/app.py"],
                "permissions": [{"owner": 584792, "group": 584792}],
            },
            "fastapi-framework/runtime": {
                "plugin": "nil",
                "stage-packages": ["ca-certificates_data"],
            },
            "fastapi-framework/logging": {
                "plugin": "nil",
                "override-build": (
                    "craftctl default\n"
                    "mkdir -p $CRAFT_PART_INSTALL/opt/promtail\n"
                    "mkdir -p $CRAFT_PART_INSTALL/etc/promtail"
                ),
                "permissions": [
                    {"path": "opt/promtail", "owner": 584792, "group": 584792},
                    {"path": "etc/promtail", "owner": 584792, "group": 584792},
                ],
            },
        },
        "services": {
            "fastapi": {
                "command": "/bin/python3 -m uvicorn app:app",
                "override": "replace",
                "startup": "enabled",
                "user": "_daemon_",
                "working-dir": "/app",
                "environment": {
                    "UVICORN_HOST": "0.0.0.0",  # noqa: S104
                },
            },
        },
    }
