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
from pathlib import Path
from typing import Any

import pytest
from rockcraft import extensions
from rockcraft.errors import ExtensionError


@pytest.fixture
def flask_extension(mock_extensions):
    extensions.register("flask-framework", extensions.FlaskFramework)


@pytest.fixture(name="flask_input_yaml")
def flask_input_yaml_fixture():
    return {
        "name": "foo-bar",
        "base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
        "extensions": ["flask-framework"],
    }


@pytest.fixture
def django_extension(mock_extensions, monkeypatch):
    extensions.register("django-framework", extensions.DjangoFramework)


@pytest.fixture(name="django_input_yaml")
def django_input_yaml_fixture():
    return {
        "name": "foo-bar",
        "base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
        "extensions": ["django-framework"],
    }


@pytest.mark.usefixtures("flask_extension")
@pytest.mark.parametrize("packages", ["other\nflask", "flask", "Flask", " flask == 99"])
@pytest.mark.parametrize(
    ("async_package", "expected_worker"), [("gevent", "gevent"), ("", "sync")]
)
def test_flask_extension_default(
    tmp_path, flask_input_yaml, packages, async_package, expected_worker
):
    full_packages = f"{packages}\n{async_package}"
    (tmp_path / "requirements.txt").write_text(full_packages)
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "static").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "test").write_text("test")
    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)
    source = applied["parts"]["flask-framework/config-files"]["source"]
    del applied["parts"]["flask-framework/config-files"]["source"]
    suffix = "share/rockcraft/extensions/flask-framework"
    assert source[-len(suffix) :].replace("\\", "/") == suffix

    assert applied == {
        "name": "foo-bar",
        "base": "ubuntu@22.04",
        "parts": {
            "flask-framework/config-files": {
                "organize": {
                    "gunicorn.conf.py": "flask/gunicorn.conf.py",
                },
                "plugin": "dump",
                "permissions": [
                    {
                        "path": "flask/gunicorn.conf.py",
                        "owner": 584792,
                        "group": 584792,
                    }
                ],
            },
            "flask-framework/dependencies": {
                "plugin": "python",
                "python-packages": ["gunicorn~=23.0"],
                "python-requirements": ["requirements.txt"],
                "source": ".",
                "stage-packages": ["python3-venv"],
                "build-environment": [],
            },
            "flask-framework/install-app": {
                "organize": {
                    "app.py": "flask/app/app.py",
                    "static": "flask/app/static",
                },
                "plugin": "dump",
                "prime": ["flask/app/app.py", "flask/app/static"],
                "source": ".",
                "stage": ["flask/app/app.py", "flask/app/static"],
                "permissions": [
                    {
                        "owner": 584792,
                        "group": 584792,
                    },
                ],
            },
            "flask-framework/runtime": {
                "plugin": "nil",
                "stage-packages": ["ca-certificates_data"],
            },
            "flask-framework/logging": {
                "plugin": "nil",
                "override-build": (
                    "craftctl default\n"
                    "mkdir -p $CRAFT_PART_INSTALL/opt/promtail\n"
                    "mkdir -p $CRAFT_PART_INSTALL/etc/promtail\n"
                    "mkdir -p $CRAFT_PART_INSTALL/var/log/flask"
                ),
                "permissions": [
                    {"path": "opt/promtail", "owner": 584792, "group": 584792},
                    {"path": "etc/promtail", "owner": 584792, "group": 584792},
                    {
                        "path": "var/log/flask",
                        "owner": 584792,
                        "group": 584792,
                    },
                ],
            },
            "flask-framework/statsd-exporter": {
                "build-snaps": ["go"],
                "plugin": "go",
                "source": "https://github.com/prometheus/statsd_exporter.git",
                "source-tag": "v0.26.0",
            },
        },
        "platforms": {"amd64": {}},
        "run_user": "_daemon_",
        "services": {
            "flask": {
                "after": ["statsd-exporter"],
                "command": "/bin/python3 -m gunicorn -c "
                f"/flask/gunicorn.conf.py 'app:app' -k [ {expected_worker} ]",
                "override": "replace",
                "startup": "enabled",
                "user": "_daemon_",
            },
            "statsd-exporter": {
                "command": (
                    "/bin/statsd_exporter --statsd.mapping-config=/statsd-mapping.conf "
                    "--statsd.listen-udp=localhost:9125 "
                    "--statsd.listen-tcp=localhost:9125"
                ),
                "override": "merge",
                "startup": "enabled",
                "summary": "statsd exporter service",
                "user": "_daemon_",
            },
        },
    }


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_prime_override(tmp_path, flask_input_yaml):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "static").mkdir()
    (tmp_path / "node_modules").mkdir()

    flask_input_yaml["parts"] = {
        "flask-framework/install-app": {
            "prime": [
                "flask/app/app.py",
                "flask/app/requirements.txt",
                "flask/app/static",
            ]
        }
    }
    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)
    install_app_part = applied["parts"]["flask-framework/install-app"]
    assert install_app_part["prime"] == [
        "flask/app/app.py",
        "flask/app/requirements.txt",
        "flask/app/static",
    ]
    assert install_app_part["organize"] == {
        "app.py": "flask/app/app.py",
        "requirements.txt": "flask/app/requirements.txt",
        "static": "flask/app/static",
    }
    assert install_app_part["stage"] == [
        "flask/app/app.py",
        "flask/app/requirements.txt",
        "flask/app/static",
    ]
    assert install_app_part["permissions"] == [
        {
            "owner": 584792,
            "group": 584792,
        },
    ]


@pytest.mark.usefixtures("flask_extension")
def test_flask_framework_exclude_prime(tmp_path, flask_input_yaml):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "static").mkdir()
    (tmp_path / "webapp").mkdir()
    (tmp_path / "test").mkdir()
    (tmp_path / "node_modules").mkdir()
    flask_input_yaml["parts"] = {
        "flask-framework/install-app": {
            "prime": [
                "- flask/app/test",
            ]
        }
    }
    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)
    install_app_part = applied["parts"]["flask-framework/install-app"]
    assert install_app_part["prime"] == ["- flask/app/test"]
    assert install_app_part["organize"] == {
        "app.py": "flask/app/app.py",
        "requirements.txt": "flask/app/requirements.txt",
        "static": "flask/app/static",
        "test": "flask/app/test",
        "webapp": "flask/app/webapp",
    }
    assert install_app_part["stage"] == [
        "flask/app/app.py",
        "flask/app/requirements.txt",
        "flask/app/static",
        "flask/app/test",
        "flask/app/webapp",
    ]
    assert install_app_part["permissions"] == [
        {
            "owner": 584792,
            "group": 584792,
        },
    ]


@pytest.mark.usefixtures("flask_extension")
def test_flask_framework_service_override(tmp_path, flask_input_yaml):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").write_text("app = object()")
    flask_input_yaml["services"] = {
        "flask": {
            "command": "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py webapp:app"
        }
    }

    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)
    assert applied["services"]["flask"] == {
        "after": ["statsd-exporter"],
        "command": "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py webapp:app",
        "override": "replace",
        "startup": "enabled",
        "user": "_daemon_",
    }


@pytest.mark.usefixtures("flask_extension")
def test_flask_framework_add_service(tmp_path, flask_input_yaml):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").write_text("app = object()")
    flask_input_yaml["services"] = {
        "foobar": {
            "command": "/bin/foobar",
            "override": "replace",
        },
    }

    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)
    assert applied["services"] == {
        "flask": {
            "after": ["statsd-exporter"],
            "command": "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py 'app:app' -k [ sync ]",
            "override": "replace",
            "startup": "enabled",
            "user": "_daemon_",
        },
        "foobar": {"command": "/bin/foobar", "override": "replace"},
        "statsd-exporter": {
            "command": (
                "/bin/statsd_exporter --statsd.mapping-config=/statsd-mapping.conf "
                "--statsd.listen-udp=localhost:9125 "
                "--statsd.listen-tcp=localhost:9125"
            ),
            "override": "merge",
            "startup": "enabled",
            "summary": "statsd exporter service",
            "user": "_daemon_",
        },
    }


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_override_parts(tmp_path, flask_input_yaml):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "foobar").touch()
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "static").mkdir()
    (tmp_path / "node_modules").mkdir()

    flask_input_yaml["parts"] = {
        "flask-framework/install-app": {"prime": ["-flask/app/foobar"]},
        "flask-framework/dependencies": {
            "python-requirements": ["requirements-jammy.txt"]
        },
    }
    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)

    assert applied["parts"]["flask-framework/install-app"]["prime"] == [
        "-flask/app/foobar"
    ]

    assert applied["parts"]["flask-framework/dependencies"] == {
        "plugin": "python",
        "python-packages": ["gunicorn~=23.0"],
        "python-requirements": ["requirements.txt", "requirements-jammy.txt"],
        "source": ".",
        "stage-packages": ["python3-venv"],
        "build-environment": [],
    }
    assert applied["parts"]["flask-framework/install-app"]["permissions"] == [
        {
            "owner": 584792,
            "group": 584792,
        },
    ]


@pytest.mark.parametrize(
    ("build_base", "expected_stage_packages", "expected_python_interpreter"),
    [
        ("ubuntu@22.04", ["python3.10-venv_ensurepip"], "python3.10"),
        ("ubuntu:22.04", ["python3.10-venv_ensurepip"], "python3.10"),
        ("ubuntu@24.04", ["python3.12-venv_ensurepip"], "python3.12"),
        ("ubuntu:24.04", ["python3.12-venv_ensurepip"], "python3.12"),
    ],
)
@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_bare(
    tmp_path, build_base, expected_stage_packages, expected_python_interpreter
):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").write_text("app = object()")
    flask_input_yaml = {
        "name": "test-app",
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": build_base,
        "platforms": {"amd64": {}},
        "parts": {"flask/install-app": {"prime": ["-flask/app/.git"]}},
    }
    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)
    assert applied["parts"]["flask-framework/runtime"] == {
        "plugin": "nil",
        "override-build": "mkdir -m 777 ${CRAFT_PART_INSTALL}/tmp\n"
        "ln -sf /usr/bin/bash ${CRAFT_PART_INSTALL}/usr/bin/sh",
        "stage-packages": ["bash_bins", "coreutils_bins", "ca-certificates_data"],
    }
    assert applied["parts"]["flask-framework/dependencies"] == {
        "plugin": "python",
        "python-packages": ["gunicorn~=23.0"],
        "python-requirements": ["requirements.txt"],
        "source": ".",
        "stage-packages": expected_stage_packages,
        "build-environment": [
            {"PARTS_PYTHON_INTERPRETER": expected_python_interpreter}
        ],
    }
    assert applied["parts"]["flask-framework/install-app"]["permissions"] == [
        {
            "owner": 584792,
            "group": 584792,
        },
    ]


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_no_requirements_txt_error(tmp_path):
    (tmp_path / "app.py").write_text("app = object()")
    flask_input_yaml = {
        "name": "test-app",
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
    }
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, flask_input_yaml)
    assert (
        str(exc.value)
        == "- missing a requirements file (requirements.txt or pyproject.toml). The flask-framework extension requires one of these files with 'flask' specified as a dependency."
    )


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_requirements_txt_no_flask_error(tmp_path):
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "requirements.txt").write_text("")
    flask_input_yaml = {
        "name": "test-app",
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
    }
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, flask_input_yaml)

    assert str(exc.value) == "- missing flask package dependency in requirements file."


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_pyproject_toml(
    tmp_path: Path, flask_input_yaml: dict[str, Any]
):
    """Test extension works with pyproject.toml"""
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            name = "test-app"
            dependencies = ["flask>=3.0", "requests"]
            """
        )
    )
    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)

    assert applied["parts"]["flask-framework/dependencies"]["python-requirements"] == []
    assert (
        applied["services"]["flask"]["command"]
        == "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py 'app:app' -k [ sync ]"
    )


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_both_requirements_files(
    tmp_path: Path, flask_input_yaml: dict[str, Any]
):
    """Test extension merges dependencies from both requirements.txt and pyproject.toml."""
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "requirements.txt").write_text("flask\nrequests")
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            name = "test-app"
            dependencies = ["gevent>=24.0"]
            """
        )
    )
    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)

    assert applied["parts"]["flask-framework/dependencies"]["python-requirements"] == [
        "requirements.txt"
    ]
    assert (
        applied["services"]["flask"]["command"]
        == "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py 'app:app' -k [ gevent ]"
    )


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_pyproject_toml_no_flask_error(
    tmp_path: Path, flask_input_yaml: dict[str, Any]
):
    """Test error when pyproject.toml exists but doesn't contain flask."""
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            name = "test-app"
            dependencies = ["requests"]
            """
        )
    )
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, flask_input_yaml)

    assert str(exc.value) == "- missing flask package dependency in requirements file."


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_both_files_flask_in_pyproject_only(
    tmp_path: Path, flask_input_yaml: dict[str, Any]
):
    """Test validation passes when flask is only in pyproject.toml but both files exist."""
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "requirements.txt").write_text("requests\ngunicorn")
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            name = "test-app"
            dependencies = ["flask>=3.0"]
            """
        )
    )
    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)
    assert applied["parts"]["flask-framework/dependencies"]["python-requirements"] == [
        "requirements.txt"
    ]
    assert (
        applied["services"]["flask"]["command"]
        == "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py 'app:app' -k [ sync ]"
    )


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_bad_app_py(tmp_path):
    bad_code = textwrap.dedent(
        """
    import flask

    app = flask.Flask()

    bad = "my value
    """
    ).strip()
    (tmp_path / "app.py").write_text(bad_code)
    (tmp_path / "requirements.txt").write_text("flask")
    flask_input_yaml = {
        "name": "test-app",
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
    }
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, flask_input_yaml)

    expected = (
        "- error parsing app.py: unterminated string literal (detected at line 5)"
    )
    assert str(exc.value) == expected


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_no_requirements_txt_no_app_py_error(tmp_path):
    flask_input_yaml = {
        "name": "test-app",
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
    }
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, flask_input_yaml)
    assert str(exc.value) == (
        "- missing a requirements file (requirements.txt or pyproject.toml). The flask-framework extension requires one of these files with 'flask' specified as a dependency.\n"
        "- Missing WSGI entrypoint in default search locations"
    )


@pytest.mark.parametrize(
    ("app_name", "app_content"),
    [
        ("app", "app = object()"),
        ("app", "from .app import app"),
        ("application", "application = object()"),
        ("application", "from .application import application"),
        ("create_app()", "def create_app(): return object()"),
        ("make_app()", "def make_app(): return object()"),
    ],
)
@pytest.mark.parametrize(
    ("file_path", "organize", "wsgi_module"),
    [
        # App in root files
        ("app.py", {"app": "flask/app/app"}, "app"),
        ("main.py", {"main": "flask/app/main"}, "main"),
        # App in module
        ("app/__init__.py", {"app": "flask/app/app"}, "app"),
        ("app/app.py", {"app": "flask/app/app"}, "app.app"),
        ("app/main.py", {"app": "flask/app/app"}, "app.main"),
        ("src/__init__.py", {"src": "flask/app/src"}, "src"),
        ("src/app.py", {"src": "flask/app/src"}, "src.app"),
        ("src/main.py", {"src": "flask/app/src"}, "src.main"),
        ("foo_bar/__init__.py", {"foo_bar": "flask/app/foo_bar"}, "foo_bar"),
        ("foo_bar/app.py", {"foo_bar": "flask/app/foo_bar"}, "foo_bar.app"),
        ("foo_bar/main.py", {"foo_bar": "flask/app/foo_bar"}, "foo_bar.main"),
    ],
)
@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_wsgi_single_entrypoint(
    tmp_path: Path,
    flask_input_yaml: dict[str, Any],
    file_path: str,
    organize: dict[str, str],
    wsgi_module: str,
    app_name: str,
    app_content: str,
):
    """Test single WSGI entrypoint discovery across all file locations and app object types."""
    (tmp_path / "requirements.txt").write_text("flask")

    (organize_value,) = organize.values()

    flask_input_yaml["parts"] = {
        "flask-framework/install-app": {"prime": [organize_value]}
    }

    # Create the file with app content
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(app_content)

    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)
    install_app_part = applied["parts"]["flask-framework/install-app"]

    # Check organize
    assert install_app_part["organize"] == organize

    # Check stage
    assert install_app_part["stage"] == [organize_value]

    # Check command
    expected_command = f"/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py '{wsgi_module}:{app_name}' -k [ sync ]"
    assert applied["services"]["flask"]["command"] == expected_command


@pytest.mark.parametrize(
    ("files", "organize", "command"),
    [
        pytest.param(
            {"app.py": "app = object()", "foo_bar/app.py": "app = object()"},
            {"app.py": "flask/app/app.py"},
            "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py 'app:app' -k [ sync ]",
            id="Multiple entrypoints, prefer top-level file",
        ),
        pytest.param(
            {"main.py": "app = object()", "src/app.py": "app = object()"},
            {"main.py": "flask/app/main.py", "src": "flask/app/src"},
            "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py 'main:app' -k [ sync ]",
            id="With two entrypoints, take the first one",
        ),
        pytest.param(
            {"src/app.py": "app = object()", "migrate.sh": "", "unknown": ""},
            {"src": "flask/app/src", "migrate.sh": "flask/app/migrate.sh"},
            "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py 'src.app:app' -k [ sync ]",
            id="Include other files beside the entrypoint",
        ),
    ],
)
@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_wsgi_multiple_entrypoints(
    tmp_path: Path,
    flask_input_yaml: dict[str, Any],
    files: dict[str, str],
    organize: dict[str, str],
    command: str,
):
    (tmp_path / "requirements.txt").write_text("flask")
    for file_path, content in files.items():
        (tmp_path / file_path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / file_path).write_text(content)
    applied = extensions.apply_extensions(tmp_path, flask_input_yaml)
    install_app_part = applied["parts"]["flask-framework/install-app"]
    assert install_app_part["organize"] == organize
    assert applied["parts"]["flask-framework/install-app"]["stage"] == list(
        install_app_part["organize"].values()
    )
    assert applied["services"]["flask"]["command"] == command


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_incorrect_prime_prefix_error(tmp_path):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").write_text("app = object()")
    flask_input_yaml = {
        "name": "test-app",
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
        "parts": {"flask-framework/install-app": {"prime": ["app.py"]}},
    }
    (tmp_path / "requirements.txt").write_text("flask")

    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, flask_input_yaml)
    assert "flask/app" in str(exc)


WSGI_FLASK_INPUT_YAML = {
    "name": "test-app",
    "extensions": ["flask-framework"],
    "base": "bare",
    "build-base": "ubuntu@22.04",
    "platforms": {"amd64": {}},
    "parts": {"flask/install-app": {"prime": ["flask/app/requirement.txt"]}},
}


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_incorrect_wsgi_path_error(tmp_path):
    (tmp_path / "app.py").write_text("flask")

    with pytest.raises(
        ExtensionError,
        match="Missing WSGI entrypoint in default search locations",
    ):
        extensions.apply_extensions(tmp_path, WSGI_FLASK_INPUT_YAML.copy())


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_incorrect_wsgi_path_error_no_app(tmp_path):
    (tmp_path / "requirements.txt").write_text("flask")

    with pytest.raises(
        ExtensionError, match="Missing WSGI entrypoint in default search locations"
    ):
        extensions.apply_extensions(tmp_path, WSGI_FLASK_INPUT_YAML.copy())


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_flask_service_override_disable_wsgi_path_check(tmp_path):
    (tmp_path / "requirements.txt").write_text("flask")

    flask_input_yaml = {
        "name": "test-app",
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
        "services": {
            "flask": {
                "command": "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py webapp:app"
            }
        },
    }

    extensions.apply_extensions(tmp_path, flask_input_yaml)


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_app_in_non_matching_directory(tmp_path):
    """Test that the extension does NOT find apps in directories that don't match the rock name.

    The flask-framework extension only searches in the directory matching the normalized
    rock name. Apps in other directories like 'backend', 'webapp', etc. should not be found.
    """
    (tmp_path / "requirements.txt").write_text("flask")

    # Create app in a directory that doesn't match the rock name
    random_dir = tmp_path / "backend"
    random_dir.mkdir()
    (random_dir / "app.py").write_text("app = object()")

    flask_input_yaml = {
        "name": "my-rock",  # Normalized to "my_rock", won't match "backend"
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
    }

    # Should raise an error because app is not in "my_rock/" directory
    with pytest.raises(
        ExtensionError, match="Missing WSGI entrypoint in default search locations"
    ):
        extensions.apply_extensions(tmp_path, flask_input_yaml)


@pytest.mark.usefixtures("django_extension")
@pytest.mark.parametrize(
    ("packages", "expected_worker"), [("Django\ngevent", "gevent"), ("Django", "sync")]
)
def test_django_extension_default(
    tmp_path, django_input_yaml, packages, expected_worker
):
    (tmp_path / "requirements.txt").write_text(packages)
    (tmp_path / "test").mkdir()
    (tmp_path / "foo_bar" / "foo_bar").mkdir(parents=True)
    (tmp_path / "foo_bar" / "foo_bar" / "wsgi.py").write_text("application = object()")

    applied = extensions.apply_extensions(tmp_path, django_input_yaml)

    source = applied["parts"]["django-framework/config-files"]["source"]
    del applied["parts"]["django-framework/config-files"]["source"]
    suffix = "share/rockcraft/extensions/django-framework"
    assert source[-len(suffix) :].replace("\\", "/") == suffix

    assert applied == {
        "name": "foo-bar",
        "base": "ubuntu@22.04",
        "parts": {
            "django-framework/config-files": {
                "organize": {"gunicorn.conf.py": "django/gunicorn.conf.py"},
                "plugin": "dump",
                "permissions": [
                    {
                        "path": "django/gunicorn.conf.py",
                        "owner": 584792,
                        "group": 584792,
                    },
                ],
            },
            "django-framework/dependencies": {
                "plugin": "python",
                "python-packages": ["gunicorn~=23.0"],
                "python-requirements": ["requirements.txt"],
                "source": ".",
                "stage-packages": ["python3-venv"],
                "build-environment": [],
            },
            "django-framework/install-app": {
                "organize": {"*": "django/app/", ".*": "django/app/"},
                "plugin": "dump",
                "source": "foo_bar",
                "stage": ["-django/app/db.sqlite3"],
                "permissions": [
                    {
                        "owner": 584792,
                        "group": 584792,
                    },
                ],
            },
            "django-framework/runtime": {
                "plugin": "nil",
                "stage-packages": ["ca-certificates_data"],
            },
            "django-framework/logging": {
                "plugin": "nil",
                "override-build": (
                    "craftctl default\n"
                    "mkdir -p $CRAFT_PART_INSTALL/opt/promtail\n"
                    "mkdir -p $CRAFT_PART_INSTALL/etc/promtail\n"
                    "mkdir -p $CRAFT_PART_INSTALL/var/log/django"
                ),
                "permissions": [
                    {"path": "opt/promtail", "owner": 584792, "group": 584792},
                    {"path": "etc/promtail", "owner": 584792, "group": 584792},
                    {
                        "path": "var/log/django",
                        "owner": 584792,
                        "group": 584792,
                    },
                ],
            },
            "django-framework/statsd-exporter": {
                "build-snaps": ["go"],
                "plugin": "go",
                "source": "https://github.com/prometheus/statsd_exporter.git",
                "source-tag": "v0.26.0",
            },
        },
        "platforms": {"amd64": {}},
        "run_user": "_daemon_",
        "services": {
            "django": {
                "after": ["statsd-exporter"],
                "command": f"/bin/python3 -m gunicorn -c /django/gunicorn.conf.py 'foo_bar.wsgi:application' -k [ {expected_worker} ]",
                "override": "replace",
                "startup": "enabled",
                "user": "_daemon_",
            },
            "statsd-exporter": {
                "command": (
                    "/bin/statsd_exporter --statsd.mapping-config=/statsd-mapping.conf "
                    "--statsd.listen-udp=localhost:9125 "
                    "--statsd.listen-tcp=localhost:9125"
                ),
                "override": "merge",
                "startup": "enabled",
                "summary": "statsd exporter service",
                "user": "_daemon_",
            },
        },
    }


@pytest.mark.usefixtures("django_extension")
def test_django_extension_override_install_app(tmp_path, django_input_yaml):
    (tmp_path / "requirements.txt").write_text("django")
    (tmp_path / "test").mkdir()
    (tmp_path / "foobar").mkdir()
    (tmp_path / "foobar" / "wsgi.py").write_text("application = object()")
    django_input_yaml["parts"] = {
        "django-framework/install-app": {
            "plugin": "dump",
            "source": ".",
            "organize": {"foobar": "django/app"},
        }
    }
    django_input_yaml["services"] = {
        "django": {
            "command": "/bin/python3 -m gunicorn -c /django/gunicorn.conf.py foobar.wsgi:application"
        }
    }
    applied = extensions.apply_extensions(tmp_path, django_input_yaml)
    assert applied["parts"]["django-framework/install-app"] == {
        "plugin": "dump",
        "source": ".",
        "organize": {"foobar": "django/app"},
        "permissions": [
            {
                "owner": 584792,
                "group": 584792,
            },
        ],
    }


WSGI_DJANGO_INPUT_YAML = {
    "name": "foobar",
    "extensions": ["django-framework"],
    "base": "bare",
    "build-base": "ubuntu@22.04",
}


@pytest.mark.usefixtures("django_extension")
def test_django_extension_incorrect_wsgi_path_error_wsgi_missing(tmp_path):
    (tmp_path / "requirements.txt").write_text("django")

    with pytest.raises(
        ExtensionError,
        match=r"unable to locate a wsgi\.py",
    ):
        extensions.apply_extensions(tmp_path, WSGI_DJANGO_INPUT_YAML.copy())


@pytest.mark.usefixtures("django_extension")
def test_django_extension_incorrect_wsgi_path_error_no_app(tmp_path):
    (tmp_path / "requirements.txt").write_text("django")
    django_project_dir = tmp_path / "foobar" / "foobar"
    django_project_dir.mkdir(parents=True)
    (django_project_dir / "wsgi.py").write_text("app = object()")

    with pytest.raises(
        ExtensionError,
        match=r"unable to locate a wsgi\.py",
    ):
        extensions.apply_extensions(tmp_path, WSGI_DJANGO_INPUT_YAML.copy())


@pytest.mark.usefixtures("django_extension")
def test_django_extension_wsgi_path_happy(tmp_path):
    (tmp_path / "requirements.txt").write_text("django")
    django_project_dir = tmp_path / "foobar" / "foobar"
    django_project_dir.mkdir(parents=True)
    (django_project_dir / "wsgi.py").write_text("app = object()")
    (django_project_dir / "wsgi.py").write_text("application = object()")

    extensions.apply_extensions(tmp_path, WSGI_DJANGO_INPUT_YAML.copy())


@pytest.mark.usefixtures("django_extension")
def test_django_extension_django_service_override_disable_wsgi_path_check(tmp_path):
    (tmp_path / "requirements.txt").write_text("flask")

    input_yaml = {
        "name": "foobar",
        "extensions": ["django-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "services": {
            "django": {
                "command": "/bin/python3 -m gunicorn -c /django/gunicorn.conf.py 'webapp:app'"
            }
        },
    }

    extensions.apply_extensions(tmp_path, input_yaml)
    extensions.apply_extensions(tmp_path, input_yaml)
    extensions.apply_extensions(tmp_path, input_yaml)
