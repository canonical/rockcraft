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

"""An extension for the Gunicorn based Python WSGI application extensions."""
import abc
import ast
import fnmatch
import os.path
import pathlib
import posixpath
import re
from typing import Any, Dict, Tuple

from overrides import override

from ..errors import ExtensionError
from .extension import Extension, get_extensions_data_dir


class _GunicornBase(Extension):
    """An extension base class for Python WSGI framework extensions."""

    @staticmethod
    @override
    def get_supported_bases() -> Tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@22.04", "ubuntu:22.04"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:
        """Check if the extension is in an experimental state."""
        return True

    @property
    @abc.abstractmethod
    def wsgi_path(self) -> str:
        """Return the wsgi path of the wsgi application."""

    @property
    @abc.abstractmethod
    def framework(self) -> str:
        """Return the wsgi framework name, e.g. flask, django."""

    @abc.abstractmethod
    def check_project(self) -> None:
        """Ensure this extension can apply to the current rockcraft project."""

    @abc.abstractmethod
    def gen_install_app_part(self) -> Dict[str, Any]:
        """Generate the content of *-framework/install-app part."""

    def _gen_parts(self) -> dict:
        """Generate the parts associated with this extension."""
        data_dir = get_extensions_data_dir()
        stage_packages = ["python3-venv"]
        build_environment = []
        if self.yaml_data["base"] == "bare":
            stage_packages = ["python3.10-venv_ensurepip"]
            build_environment = [{"PARTS_PYTHON_INTERPRETER": "python3.10"}]

        parts: Dict[str, Any] = {
            f"{self.framework}-framework/dependencies": {
                "plugin": "python",
                "stage-packages": stage_packages,
                "source": ".",
                "python-packages": ["gunicorn"],
                "python-requirements": ["requirements.txt"],
                "build-environment": build_environment,
            },
            f"{self.framework}-framework/install-app": self.gen_install_app_part(),
            f"{self.framework}-framework/config-files": {
                "plugin": "dump",
                "source": str(data_dir / f"{self.framework}-framework"),
                "organize": {
                    "gunicorn.conf.py": f"{self.framework}/gunicorn.conf.py",
                },
            },
            f"{self.framework}-framework/statsd-exporter": {
                "build-snaps": ["go"],
                "source-tag": "v0.26.0",
                "plugin": "go",
                "source": "https://github.com/prometheus/statsd_exporter.git",
            },
        }
        if self.yaml_data["base"] == "bare":
            parts[f"{self.framework}-framework/runtime"] = {
                "plugin": "nil",
                "override-build": "mkdir -m 777 ${CRAFT_PART_INSTALL}/tmp",
                "stage-packages": [
                    "bash_bins",
                    "coreutils_bins",
                    "ca-certificates_data",
                ],
            }
        else:
            parts[f"{self.framework}-framework/runtime"] = {
                "plugin": "nil",
                "stage-packages": ["ca-certificates_data"],
            }
        return parts

    @override
    def get_root_snippet(self) -> Dict[str, Any]:
        """Fill in some default root components.

        Default values:
          - run_user: _daemon_
          - build-base: ubuntu:22.04 (only if user specify bare without a build-base)
          - platform: amd64
          - services: a service to run the Gunicorn server
          - parts: see _GunicornBase._gen_parts
        """
        self.check_project()
        snippet: Dict[str, Any] = {
            "run_user": "_daemon_",
            "services": {
                self.framework: {
                    "override": "replace",
                    "startup": "enabled",
                    "command": f"/bin/python3 -m gunicorn -c /{self.framework}/gunicorn.conf.py {self.wsgi_path}",
                    "after": ["statsd-exporter"],
                    "user": "_daemon_",
                },
                "statsd-exporter": {
                    "override": "merge",
                    "command": (
                        "/bin/statsd_exporter --statsd.mapping-config=/statsd-mapping.conf "
                        "--statsd.listen-udp=localhost:9125 "
                        "--statsd.listen-tcp=localhost:9125"
                    ),
                    "summary": "statsd exporter service",
                    "startup": "enabled",
                    "user": "_daemon_",
                },
            },
        }
        snippet["parts"] = self._gen_parts()
        return snippet

    @override
    def get_part_snippet(self) -> Dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}

    @override
    def get_parts_snippet(self) -> Dict[str, Any]:
        """Return the parts to add to parts."""
        return {}

    def has_global_variable(
        self, source_file: pathlib.Path, variable_name: str
    ) -> bool:
        """Check the given Python source code has a global variable defined."""
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == variable_name:
                        return True
            if isinstance(node, ast.ImportFrom):
                for name in node.names:
                    if (name.asname is not None and name.asname == variable_name) or (
                        name.asname is None and name.name == variable_name
                    ):
                        return True
        return False


class FlaskFramework(_GunicornBase):
    """An extension for constructing Python applications based on the Flask framework."""

    @property
    @override
    def wsgi_path(self) -> str:
        """Return the wsgi path of the wsgi application."""
        return "app:app"

    @property
    @override
    def framework(self) -> str:
        """Return the wsgi framework name, e.g. flask, django."""
        return "flask"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:
        """Check if the extension is in an experimental state."""
        return False

    @override
    def gen_install_app_part(self) -> Dict[str, Any]:
        source_files = [f.name for f in sorted(self.project_root.iterdir())]
        # if prime is not in exclude mode, use it to generate the stage and organize
        if self._app_prime and self._app_prime[0] and self._app_prime[0][0] != "-":
            renaming_map = {
                os.path.relpath(file, f"{self.framework}/app"): file
                for file in self._app_prime
            }
        else:
            renaming_map = {
                f: posixpath.join(f"{self.framework}/app", f)
                for f in source_files
                if not any(
                    fnmatch.fnmatch(f, p)
                    for p in ("node_modules", ".git", ".yarn", "*.rock")
                )
            }

        return {
            "plugin": "dump",
            "source": ".",
            "organize": renaming_map,
            "stage": list(renaming_map.values()),
            "prime": self._app_prime,
        }

    @property
    def _app_prime(self) -> list[str]:
        """Return the prime list for the Flask project."""
        user_prime = (
            self.yaml_data.get("parts", {})
            .get("flask-framework/install-app", {})
            .get("prime", [])
        )
        if not all(re.match("-? *flask/app", p) for p in user_prime):
            raise ExtensionError(
                "flask-framework extension requires the 'prime' entry in the "
                "flask-framework/install-app part to start with flask/app",
                doc_slug="/reference/extensions/flask-framework",
                logpath_report=False,
            )
        if not user_prime:
            user_prime = [
                f"flask/app/{f}"
                for f in (
                    "app",
                    "app.py",
                    "migrate",
                    "migrate.sh",
                    "migrate.py",
                    "static",
                    "templates",
                )
                if (self.project_root / f).exists()
            ]
        return user_prime

    def _wsgi_path_error_messages(self) -> list[str]:
        """Ensure the extension can infer the WSGI path of the Flask application."""
        app_file = self.project_root / "app.py"
        if not app_file.exists():
            return [
                "flask application can not be imported from app:app, no app.py file found in the project root."
            ]
        try:
            has_app = self.has_global_variable(app_file, "app")
        except SyntaxError as err:
            return [f"error parsing app.py: {err.msg}"]

        if not has_app:
            return [
                "flask application can not be imported from app:app in app.py in the project root."
            ]

        return []

    def _requirements_txt_error_messages(self) -> list[str]:
        """Ensure the requirements.txt file is correct."""
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            return [
                "missing a requirements.txt file. The flask-framework extension requires this file with 'flask' specified as a dependency."
            ]

        requirements_lines = requirements_file.read_text(encoding="utf-8").splitlines()
        if not any(("flask" in line.lower() for line in requirements_lines)):
            return ["missing flask package dependency in requirements.txt file."]

        return []

    @override
    def check_project(self) -> None:
        """Ensure this extension can apply to the current rockcraft project."""
        error_messages = self._requirements_txt_error_messages()
        if not self.yaml_data.get("services", {}).get("flask", {}).get("command"):
            error_messages += self._wsgi_path_error_messages()
        if error_messages:
            raise ExtensionError(
                "\n".join("- " + message for message in error_messages),
                doc_slug="/reference/extensions/flask-framework",
                logpath_report=False,
            )


class DjangoFramework(_GunicornBase):
    """An extension for constructing Python applications based on the Django framework."""

    @property
    def name(self) -> str:
        """Return the normalized name of the rockcraft project."""
        return self.yaml_data["name"].replace("-", "_").lower()

    @property
    def default_wsgi_path(self) -> str:
        """Return the default wsgi path for the Django project."""
        return f"{self.name}.wsgi:application"

    @property
    @override
    def wsgi_path(self) -> str:
        """Return the wsgi path of the wsgi application."""
        return self.default_wsgi_path

    @property
    @override
    def framework(self) -> str:
        """Return the wsgi framework name, e.g. flask, django."""
        return "django"

    @override
    def gen_install_app_part(self) -> Dict[str, Any]:
        """Return the prime list for the Flask project."""
        if "django-framework/install-app" not in self.yaml_data.get("parts", {}):
            return {
                "plugin": "dump",
                "source": self.name,
                "organize": {"*": "django/app/", ".*": "django/app/"},
            }
        return {}

    def _check_wsgi_path(self) -> None:
        wsgi_file = self.project_root / self.name / self.name / "wsgi.py"
        if not wsgi_file.exists():
            raise ExtensionError(
                f"django application can not be imported from {self.default_wsgi_path}, "
                f"no wsgi.py file found in the project directory ({str(wsgi_file.parent)})."
            )
        if not self.has_global_variable(wsgi_file, "application"):
            raise ExtensionError(
                "django application can not be imported from {self.default_wsgi_path}, "
                "no variable named application in application.py"
            )

    @override
    def check_project(self) -> None:
        """Ensure this extension can apply to the current rockcraft project."""
        if not (self.project_root / "requirements.txt").exists():
            raise ExtensionError(
                "missing requirements.txt file, django-framework extension "
                "requires this file with Django specified as a dependency"
            )
        if not self.yaml_data.get("services", {}).get("django", {}).get("command"):
            self._check_wsgi_path()
