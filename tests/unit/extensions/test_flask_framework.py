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
    extensions.register("flask-framework", extensions.flask_framework.FlaskFramework)


@pytest.fixture(name="input_yaml")
def input_yaml_fixture():
    return {"base": "ubuntu:22.04", "extensions": ["flask-framework"]}


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension(tmp_path, input_yaml):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "static").mkdir()
    (tmp_path / "node_modules").mkdir()

    input_yaml["parts"] = {
        "flask/install-app": {
            "prime": [
                "flask/app/app.py",
                "flask/app/requirements.txt",
                "flask/app/static",
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
        "working-dir": "/flask/app",
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
                "flask/app/app.py",
                "flask/app/requirements.txt",
                "flask/app/static",
            ],
            "organize": {
                "app.py": "flask/app/app.py",
                "static": "flask/app/static",
                "requirements.txt": "flask/app/requirements.txt",
            },
            "plugin": "dump",
            "prime": [
                "flask/app/app.py",
                "flask/app/requirements.txt",
                "flask/app/static",
            ],
        },
    }


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_overwrite(tmp_path, input_yaml):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "foobar").touch()
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "static").mkdir()
    (tmp_path / "node_modules").mkdir()

    input_yaml["parts"] = {
        "flask/install-app": {"prime": ["-flask/app/foobar"]},
        "flask/dependencies": {"python-requirements": ["requirements-jammy.txt"]},
    }
    input_yaml["services"] = {
        "foobar": {
            "command": "/bin/foobar",
            "override": "replace",
        },
    }
    applied = extensions.apply_extensions(tmp_path, input_yaml)

    assert applied["services"] == {
        "flask": {
            "command": "/bin/python3 -m gunicorn --bind 0.0.0.0:8000 app:app",
            "override": "replace",
            "startup": "enabled",
            "user": "_daemon_",
            "working-dir": "/flask/app",
        },
        "foobar": {
            "command": "/bin/foobar",
            "override": "replace",
        },
    }
    assert applied["parts"]["flask/install-app"]["prime"] == ["-flask/app/foobar"]

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
    (tmp_path / "app.py").write_text("app = object()")
    input_yaml = {
        "extensions": ["flask-framework"],
        "base": "bare",
        "parts": {"flask/install-app": {"prime": ["-flask/app/.git"]}},
    }
    applied = extensions.apply_extensions(tmp_path, input_yaml)
    assert applied["parts"]["flask/container-processing"] == {
        "plugin": "nil",
        "source": ".",
        "override-build": "mkdir -m 777 ${CRAFT_PART_INSTALL}/tmp",
    }
    assert applied["build-base"] == "ubuntu:22.04"


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_no_requirements_txt_error(tmp_path):
    input_yaml = {"extensions": ["flask-framework"], "base": "bare"}
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "requirements.txt" in str(exc)


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_no_install_app_part_error(tmp_path):
    input_yaml = {"extensions": ["flask-framework"], "base": "bare"}

    (tmp_path / "requirements.txt").write_text("flask")

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "flask/install-app" in str(exc)


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_no_install_app_prime_error(tmp_path):
    input_yaml = {
        "extensions": ["flask-framework"],
        "base": "bare",
        "parts": {"flask/install-app": {}},
    }
    (tmp_path / "requirements.txt").write_text("flask")

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "flask/install-app" in str(exc)


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_empty_install_app_prime_error(tmp_path):
    input_yaml = {
        "extensions": ["flask-framework"],
        "base": "bare",
        "parts": {"flask/install-app": {"prime": []}},
    }
    (tmp_path / "requirements.txt").write_text("flask")

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "flask/install-app" in str(exc)


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_incorrect_install_app_prime_prefix_error(tmp_path):
    input_yaml = {
        "extensions": ["flask-framework"],
        "base": "bare",
        "parts": {"flask/install-app": {"prime": ["requirement.txt"]}},
    }
    (tmp_path / "requirements.txt").write_text("flask")

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "flask/app" in str(exc)


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_incorrect_wsgi_path_error(tmp_path):
    input_yaml = {
        "extensions": ["flask-framework"],
        "base": "bare",
        "parts": {"flask/install-app": {"prime": ["flask/app/requirement.txt"]}},
    }
    (tmp_path / "requirements.txt").write_text("flask")

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "app:app" in str(exc)

    (tmp_path / "app.py").write_text("flask")

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)
    assert "app:app" in str(exc)
