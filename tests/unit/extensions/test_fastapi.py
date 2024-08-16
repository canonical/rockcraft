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
def flask_input_yaml_fixture():
    return {
        "name": "foo-bar",
        "base": "ubuntu@24.04",
        "platforms": {"amd64": {}},
        "extensions": ["fastapi-framework"],
    }


@pytest.fixture
def fastapi_extension(mock_extensions, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    extensions.register("fastapi-framework", extensions.FastAPIFramework)


@pytest.mark.usefixtures("fastapi_extension")
@pytest.mark.parametrize("packages", ["other\nfastapi", "fastapi", "Fastapi", " fastapi == 99", "starlette"])
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
                "plugin": "python",
                "stage-packages": ["python3-venv"],
                "source": ".",
                "python-packages": ["uvicorn"],
                "python-requirements": ["requirements.txt"],
                "build-environment": [],
            },
            "fastapi-framework/install-app": {
                "plugin": "dump",
                "source": ".",
                "organize": {
                    "app.py": "app/app.py",
                },
                "stage": ["app/app.py"],
            },
            "fastapi-framework/runtime": {
                "plugin": "nil",
                "stage-packages": ["ca-certificates_data"],
            },
        },
        "services": {
            "fastapi": {
                "command": "/bin/python3 -m uvicorn app:app",
                "override": "replace",
                "startup": "enabled",
                "user": "_daemon_",
                "working-dir": "/app",
            },
        },
    }


@pytest.mark.parametrize(
    "files,organize,command",
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


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_wrong_asgi_entrypoint(
    tmp_path, fastapi_input_yaml
):
    (tmp_path / "requirements.txt").write_text("fastapi")
    (tmp_path / "app.py").write_text("app = ")
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    assert (
        "- Syntax error in  python file in ASGI search path" in str(exc.value)
    )
    assert "invalid syntax (app.py, line 1)" in str(exc.value)

@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_missing_asgi_entrypoint(
    tmp_path, fastapi_input_yaml
):
    (tmp_path / "requirements.txt").write_text("fastapi")
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, fastapi_input_yaml)
    assert (
        "- missing ASGI entrypoint" in str(exc.value)
    )


@pytest.mark.usefixtures("fastapi_extension")
def test_fastapi_missing_requirements_txt(
    tmp_path, fastapi_input_yaml
):
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
        "- missing ASGI entrypoint"
    )


# something similar as in test_gunicorn for:
#  test_flask_framework_exclude_prime
#  test_flask_framework_service_override
#  test_flask_extension_override_parts
#  test_flask_extension_bare
#  test_flask_extension_incorrect_prime_prefix_error
#  test_flask_extension_flask_service_override_disable_wsgi_path_check
