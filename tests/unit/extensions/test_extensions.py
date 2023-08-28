# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
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

from rockcraft import errors, extensions
from rockcraft.project import load_project
from tests.unit.testing.extensions import (
    FULL_EXTENSION_YAML,
    ExperimentalExtension,
    FakeExtension,
    FullExtension,
    InvalidPartExtension,
)


@pytest.fixture
def fake_extensions(mock_extensions):
    extensions.register(FakeExtension.NAME, FakeExtension)
    extensions.register(ExperimentalExtension.NAME, ExperimentalExtension)
    extensions.register(InvalidPartExtension.NAME, InvalidPartExtension)
    extensions.register(FullExtension.NAME, FullExtension)


@pytest.fixture
def input_yaml():
    return {"base": "ubuntu:22.04"}


def test_experimental_with_env(fake_extensions, tmp_path, input_yaml, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    input_yaml["extensions"] = [ExperimentalExtension.NAME]
    project_root = tmp_path
    extensions.apply_extensions(project_root, input_yaml)


def test_experimental_no_env(fake_extensions, tmp_path, input_yaml):
    input_yaml["extensions"] = [ExperimentalExtension.NAME]
    with pytest.raises(errors.ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)

    expected_message = f"Extension is experimental: '{ExperimentalExtension.NAME}'"
    assert str(exc.value) == expected_message


@pytest.mark.parametrize("base", ("ubuntu:20.04", "bare"))
def test_wrong_base(fake_extensions, tmp_path, input_yaml, base):
    input_yaml["extensions"] = [FakeExtension.NAME]
    input_yaml["base"] = base
    with pytest.raises(errors.ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)

    expected_message = (
        f"Extension '{FakeExtension.NAME}' does not support base: '{base}'"
    )
    assert str(exc.value) == expected_message


def test_invalid_parts(fake_extensions, tmp_path, input_yaml):
    input_yaml["extensions"] = [InvalidPartExtension.NAME]

    with pytest.raises(ValueError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)

    assert "Extension has invalid part names" in str(exc.value)


def test_apply_extensions(fake_extensions, tmp_path, input_yaml):
    input_yaml["services"] = {"my-service": {"command": "foo", "override": "merge"}}
    input_yaml["extensions"] = [FullExtension.NAME]
    input_yaml["parts"] = {
        "my-part": {"plugin": "nil", "source": None, "stage-packages": ["old-package"]}
    }

    applied = extensions.apply_extensions(tmp_path, input_yaml)

    # Root snippet extends the project's
    services = applied["services"]
    assert services["my-service"] == {
        "command": "foo",
        "override": "merge",
    }
    assert services["full-extension-service"] == {
        "command": "fake command",
        "override": "replace",
    }

    # Part snippet extends the existing part
    parts = applied["parts"]
    assert parts["my-part"]["stage-packages"] == [
        "new-package-1",
        "old-package",
    ]

    # New part
    assert parts[f"{FullExtension.NAME}/new-part"] == {"plugin": "nil", "source": None}


def test_project_load_extensions(fake_extensions, tmp_path):
    """Test that load_project() correctly applies the extensions."""
    rockcraft_yaml = tmp_path / "rockcraft.yaml"
    rockcraft_yaml.write_text(FULL_EXTENSION_YAML)

    project = load_project(rockcraft_yaml)

    # Root snippet extends the project's
    services = project["services"]
    assert services is not None
    assert len(services) == 2
    assert services["full-extension-service"]["command"] == "fake command"
    assert services["full-extension-service"]["override"] == "replace"
    assert services["my-service"]["command"] == "foo"
    assert services["my-service"]["override"] == "merge"

    # Part snippet extends the existing part
    parts = project["parts"]
    assert parts["foo"]["stage-packages"] == [
        "new-package-1",
        "old-package",
    ]

    # New part
    assert parts[f"{FullExtension.NAME}/new-part"] == {"plugin": "nil", "source": None}


def test_flask_extensions(fake_extensions, tmp_path, input_yaml, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    extensions.register("flask", extensions.flask.Flask)

    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").touch()
    (tmp_path / "static").mkdir()
    (tmp_path / "node_modules").mkdir()

    input_yaml["extensions"] = ["flask"]

    applied = extensions.apply_extensions(tmp_path, input_yaml)

    assert applied["run_user"] == "_daemon_"
    assert applied["platforms"] == {"amd64": {}}

    # Root snippet extends the project's
    services = applied["services"]
    assert services["flask"] == {
        "command": "/bin/python3 -m gunicorn --bind 0.0.0.0:8000 app:app",
        "override": "replace",
        "startup": "enabled",
        "user": "_daemon_",
        "working-dir": "/srv/flask/app",
    }

    parts = applied["parts"]
    assert sorted(parts["flask/install-app"]["stage"]) == [
        "srv/flask/app/app.py",
        "srv/flask/app/requirements.txt",
        "srv/flask/app/static",
    ]
    del parts["flask/install-app"]["stage"]
    assert parts == {
        "flask/dependencies": {
            "source": ".",
            "plugin": "python",
            "python-requirements": ["requirements.txt"],
            "stage-packages": ["python3-venv"],
            "python-packages": ["gunicorn"],
        },
        "flask/install-app": {
            "source": ".",
            "organize": {
                "app.py": "srv/flask/app/app.py",
                "static": "srv/flask/app/static",
                "requirements.txt": "srv/flask/app/requirements.txt",
            },
            "plugin": "dump",
        },
    }


def test_flask_extensions_overwrite(fake_extensions, tmp_path, input_yaml, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    extensions.register("flask", extensions.flask.Flask)

    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "foobar").touch()
    (tmp_path / "webapp").mkdir()
    (tmp_path / "webapp/app.py").touch()
    (tmp_path / "static").mkdir()
    (tmp_path / "node_modules").mkdir()

    input_yaml["extensions"] = ["flask"]
    input_yaml["parts"] = {"flask/install-app": {"prime": ["-srv/flask/app/foobar"]}}
    input_yaml["services"] = {
        "flask": {
            "command": "/bin/python3 -m gunicorn --bind 0.0.0.0:8000 webapp.app:app"
        }
    }
    applied = extensions.apply_extensions(tmp_path, input_yaml)

    assert applied["services"] == {
        "flask": {
            "command": "/bin/python3 -m gunicorn --bind 0.0.0.0:8000 webapp.app:app",
            "override": "replace",
            "startup": "enabled",
            "user": "_daemon_",
            "working-dir": "/srv/flask/app",
        }
    }
    assert applied["parts"]["flask/install-app"]["prime"] == ["-srv/flask/app/foobar"]


def test_flask_extensions_bare(fake_extensions, tmp_path, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    extensions.register("flask", extensions.flask.Flask)

    (tmp_path / "requirements.txt").write_text("flask")
    input_yaml = {"extensions": ["flask"], "base": "bare"}
    applied = extensions.apply_extensions(tmp_path, input_yaml)
    assert applied["parts"]["flask/container-processing"] == {
        "plugin": "nil",
        "source": ".",
        "override-prime": "craftctl default\nmkdir -p tmp\nchmod 777 tmp",
    }
