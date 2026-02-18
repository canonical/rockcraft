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


@pytest.fixture
def flask_extension(mock_extensions):
    extensions.register("flask-framework", extensions.FlaskFramework)


@pytest.fixture(name="flask_input_yaml")
def flask_input_yaml_fixture():
    return {
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
                f"/flask/gunicorn.conf.py app:app -k [ {expected_worker} ]",
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
            "command": "/bin/python3 -m gunicorn -c /flask/gunicorn.conf.py app:app -k [ sync ]",
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
        "stage-packages": [
            "bash_bins",
            "coreutils_bins",
            "ca-certificates_data",
            "libstdc++6",
        ],
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
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
    }
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, flask_input_yaml)
    assert (
        str(exc.value)
        == "- missing a requirements.txt file. The flask-framework extension requires this file with 'flask' specified as a dependency."
    )


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_requirements_txt_no_flask_error(tmp_path):
    (tmp_path / "app.py").write_text("app = object()")
    (tmp_path / "requirements.txt").write_text("")
    flask_input_yaml = {
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
    }
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, flask_input_yaml)

    assert (
        str(exc.value) == "- missing flask package dependency in requirements.txt file."
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
        "extensions": ["flask-framework"],
        "base": "bare",
        "build-base": "ubuntu@22.04",
        "platforms": {"amd64": {}},
    }
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, flask_input_yaml)
    assert str(exc.value) == (
        "- missing a requirements.txt file. The flask-framework extension requires this file with 'flask' specified as a dependency.\n"
        "- flask application can not be imported from app:app, no app.py file found in the project root."
    )


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_incorrect_prime_prefix_error(tmp_path):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").write_text("app = object()")
    flask_input_yaml = {
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
        match="the global variable 'app' was not found in app.py in the project root.",
    ):
        extensions.apply_extensions(tmp_path, WSGI_FLASK_INPUT_YAML.copy())


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_incorrect_wsgi_path_error_no_app(tmp_path):
    (tmp_path / "requirements.txt").write_text("flask")

    with pytest.raises(ExtensionError, match="app:app, no app.py"):
        extensions.apply_extensions(tmp_path, WSGI_FLASK_INPUT_YAML.copy())


@pytest.mark.usefixtures("flask_extension")
def test_flask_extension_flask_service_override_disable_wsgi_path_check(tmp_path):
    (tmp_path / "requirements.txt").write_text("flask")

    flask_input_yaml = {
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
        "base": "ubuntu@22.04",
        "name": "foo-bar",
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
                "command": f"/bin/python3 -m gunicorn -c /django/gunicorn.conf.py foo_bar.wsgi:application -k [ {expected_worker} ]",
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
        ExtensionError, match=r"wsgi:application, no wsgi\.py file found"
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
        match=r"wsgi:application, no variable named 'application' in wsgi.py",
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
                "command": "/bin/python3 -m gunicorn -c /django/gunicorn.conf.py webapp:app"
            }
        },
    }

    extensions.apply_extensions(tmp_path, input_yaml)
    extensions.apply_extensions(tmp_path, input_yaml)
    extensions.apply_extensions(tmp_path, input_yaml)
