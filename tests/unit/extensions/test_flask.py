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

from rockcraft import extensions
from rockcraft.errors import ExtensionError


@pytest.fixture
def flask_extension(mock_extensions, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    extensions.register("flask", extensions.flask.Flask)


@pytest.fixture(name="input_yaml")
def input_yaml_fixture():
    return {"base": "ubuntu:22.04", "extensions": ["flask"]}


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension(tmp_path, input_yaml):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").touch()
    (tmp_path / "static").mkdir()
    (tmp_path / "node_modules").mkdir()

    input_yaml["parts"] = {
        "flask/install-app": {
            "prime": [
                "srv/flask/app/app.py",
                "srv/flask/app/requirements.txt",
                "srv/flask/app/static",
            ]
        }
    }
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
            "stage": [
                "srv/flask/app/app.py",
                "srv/flask/app/node_modules",
                "srv/flask/app/requirements.txt",
                "srv/flask/app/static",
            ],
            "organize": {
                "app.py": "srv/flask/app/app.py",
                "node_modules": "srv/flask/app/node_modules",
                "static": "srv/flask/app/static",
                "requirements.txt": "srv/flask/app/requirements.txt",
            },
            "plugin": "dump",
            "prime": [
                "srv/flask/app/app.py",
                "srv/flask/app/requirements.txt",
                "srv/flask/app/static",
            ],
        },
    }


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_overwrite(tmp_path, input_yaml):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "foobar").touch()
    (tmp_path / "webapp").mkdir()
    (tmp_path / "webapp/app.py").touch()
    (tmp_path / "static").mkdir()
    (tmp_path / "node_modules").mkdir()

    input_yaml["parts"] = {
        "flask/install-app": {"prime": ["-srv/flask/app/foobar"]},
        "flask/dependencies": {"python-requirements": ["requirements-jammy.txt"]},
    }
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

    assert applied["parts"]["flask/dependencies"] == {
        "plugin": "python",
        "python-packages": ["gunicorn"],
        "python-requirements": ["requirements.txt", "requirements-jammy.txt"],
        "source": ".",
        "stage-packages": ["python3-venv"],
    }


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_bare(tmp_path):
    (tmp_path / "requirements.txt").write_text("flask")
    input_yaml = {
        "extensions": ["flask"],
        "base": "bare",
        "parts": {"flask/install-app": {"prime": ["-srv/flask/app/.git"]}},
    }
    applied = extensions.apply_extensions(tmp_path, input_yaml)
    assert applied["parts"]["flask/container-processing"] == {
        "plugin": "nil",
        "source": ".",
        "override-build": "mkdir -m 777 ${CRAFT_PART_INSTALL}/tmp",
    }
    assert applied["build-base"] == "ubuntu:22.04"


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_error(tmp_path):
    input_yaml = {"extensions": ["flask"], "base": "bare"}
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "requirements.txt" in str(exc)

    (tmp_path / "requirements.txt").write_text("flask")

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "flask/install-app" in str(exc)

    input_yaml["parts"] = {"flask/install-app": {}}

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "flask/install-app" in str(exc)

    input_yaml["parts"] = {"flask/install-app": {"prime": []}}

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "flask/install-app" in str(exc)

    input_yaml["parts"] = {"flask/install-app": {"prime": ["requirement.txt"]}}

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "srv/flask/app" in str(exc)
