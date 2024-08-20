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
def test_fastapi_extension_default(tmp_path, fastapi_input_yaml):
    (tmp_path / "requirements.txt").write_text("fastapi")
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

# TODO CHECK ALL POSSIBLE ENTRYPOINTS
# TODO CHECK ENTRYPOINT WITH WRONG AST
# TODO CHECK MISSING ENTRYPOINT
# TODO CHECK MISSING REQUIREMENTS.TXT
