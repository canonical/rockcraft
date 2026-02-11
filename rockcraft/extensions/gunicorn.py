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
import contextlib
import fnmatch
import os.path
import posixpath
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

try:
    # Available in Python 3.11 and later
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:
    # Use the backported tomli package
    import tomli as tomllib  # type: ignore[import-not-found]

from overrides import override  # type: ignore[reportUnknownVariableType]
from packaging.requirements import InvalidRequirement, Requirement

from rockcraft.errors import ExtensionError
from rockcraft.usernames import SUPPORTED_GLOBAL_USERNAMES

from ._python_utils import (
    find_entrypoint_with_factory,
    find_entrypoint_with_variable,
    has_global_variable,
)
from ._utils import find_ubuntu_base_python_version
from .app_parts import gen_logging_part
from .extension import Extension, get_extensions_data_dir

USER_UID: int = SUPPORTED_GLOBAL_USERNAMES["_daemon_"]["uid"]


class _GunicornBase(Extension):
    """An extension base class for Python WSGI framework extensions."""

    @staticmethod
    @override
    def get_supported_bases() -> tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@22.04", "ubuntu:22.04", "ubuntu@24.04"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:  # noqa: ARG004 (unused arg)
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
    def gen_install_app_part(self) -> dict[str, Any]:
        """Generate the content of *-framework/install-app part."""

    def _gen_parts(self) -> dict[str, Any]:
        """Generate the parts associated with this extension."""
        data_dir = get_extensions_data_dir()
        stage_packages = ["python3-venv"]
        build_environment = []
        if self.yaml_data["base"] == "bare":
            try:
                python_version = find_ubuntu_base_python_version(
                    base=self.yaml_data["build-base"]
                )
            except NotImplementedError:
                raise ExtensionError(
                    "Unable to determine the Python version for the base",
                    doc_slug="/reference/extensions/gunicorn",
                    logpath_report=False,
                )
            stage_packages = [f"python{python_version}-venv_ensurepip"]
            build_environment = [
                {"PARTS_PYTHON_INTERPRETER": f"python{python_version}"}
            ]

        python_requirements: list[str] = []
        if (self.project_root / "requirements.txt").exists():
            python_requirements.append("requirements.txt")

        parts: dict[str, Any] = {
            f"{self.framework}-framework/dependencies": {
                "plugin": "python",
                "stage-packages": stage_packages,
                "source": ".",
                "python-packages": ["gunicorn~=23.0"],
                "python-requirements": python_requirements,
                "build-environment": build_environment,
            },
            f"{self.framework}-framework/install-app": {
                **self.gen_install_app_part(),
                "permissions": [{"owner": USER_UID, "group": USER_UID}],
            },
            f"{self.framework}-framework/config-files": {
                "plugin": "dump",
                "source": str(data_dir / f"{self.framework}-framework"),
                "organize": {
                    "gunicorn.conf.py": f"{self.framework}/gunicorn.conf.py",
                },
                "permissions": [
                    {
                        "path": f"{self.framework}/gunicorn.conf.py",
                        "owner": USER_UID,
                        "group": USER_UID,
                    },
                ],
            },
            f"{self.framework}-framework/statsd-exporter": {
                "build-snaps": ["go"],
                "source-tag": "v0.26.0",
                "plugin": "go",
                "source": "https://github.com/prometheus/statsd_exporter.git",
            },
            f"{self.framework}-framework/logging": gen_logging_part(
                override_build_lines=[
                    f"mkdir -p $CRAFT_PART_INSTALL/var/log/{self.framework}"
                ],
                permissions=[
                    {
                        "path": f"var/log/{self.framework}",
                        "owner": USER_UID,
                        "group": USER_UID,
                    }
                ],
            ),
        }
        if self.yaml_data["base"] == "bare":
            parts[f"{self.framework}-framework/runtime"] = {
                "plugin": "nil",
                "override-build": "mkdir -m 777 ${CRAFT_PART_INSTALL}/tmp\n"
                "ln -sf /usr/bin/bash ${CRAFT_PART_INSTALL}/usr/bin/sh",
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

    def _requirements(self) -> set[str]:
        """Return the content of the detected requirements file.

        Checks both requirements.txt and pyproject.toml if they exist,
        merging dependencies from both files.
        """
        requirements_file = self.project_root / "requirements.txt"
        pyproject_file = self.project_root / "pyproject.toml"

        requirements: set[str] = set()

        if requirements_file.exists():
            for line in requirements_file.read_text().splitlines():
                with contextlib.suppress(InvalidRequirement):
                    req = Requirement(line)
                    requirements.add(req.name.lower())

        if pyproject_file.exists():
            with pyproject_file.open("rb") as f:
                pyproject_data = cast(
                    dict[str, Any],
                    tomllib.load(f),  # type: ignore[reportUnknownMemberType]
                )

            deps = cast(
                list[str], pyproject_data.get("project", {}).get("dependencies", [])
            )
            for line in deps:
                with contextlib.suppress(InvalidRequirement):
                    req = Requirement(line)
                    requirements.add(req.name.lower())
        return requirements

    def _worker_class(self) -> str:
        """Return the Gunicorn worker class based on project dependencies.

        If the project's dependencies include `gevent`, use the `gevent` worker.
        Otherwise default to `sync`.
        """
        requirements = self._requirements()
        if "gevent" in requirements:
            return "gevent"
        return "sync"

    @override
    def get_root_snippet(self) -> dict[str, Any]:
        """Fill in some default root components.

        Default values:
          - run_user: _daemon_
          - build-base: ubuntu:24.04 (only if user specify bare without a build-base)
          - platform: amd64
          - services: a service to run the Gunicorn server
          - parts: see _GunicornBase._gen_parts
        """
        self.check_project()
        snippet: dict[str, Any] = {
            "run_user": "_daemon_",
            "services": {
                self.framework: {
                    "override": "replace",
                    "startup": "enabled",
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
        # If the user has overridden the service command, do not try to add it.
        if (
            not self.yaml_data.get("services", {})
            .get(self.framework, {})
            .get("command")
        ):
            snippet["services"][self.framework]["command"] = (
                f"/bin/python3 -m gunicorn -c /{self.framework}/gunicorn.conf.py '{self.wsgi_path}' -k [ {self._worker_class()} ]"
            )
        snippet["parts"] = self._gen_parts()
        return snippet

    @override
    def get_part_snippet(self) -> dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}

    @override
    def get_parts_snippet(self) -> dict[str, Any]:
        """Return the parts to add to parts."""
        return {}


class FlaskFramework(_GunicornBase):
    """An extension for constructing Python applications based on the Flask framework."""

    @property
    def name(self) -> str:
        """Return the normalized name of the rockcraft project."""
        return self.yaml_data["name"].replace("-", "_").lower()

    @property
    @override
    def wsgi_path(self) -> str:
        """Return the wsgi path of the wsgi application.

        Infers an entrypoint by scanning the project's source tree.

        This extension will:
        - Search common names (`app`, `application`).
        - Search factory function definitions (`create_app`, `make_app`).

        This extension does not:
        - Validate runtime types.
        - Fallback to any singular `Flask` app if only one is found.

        Reference: Flask's CLI uses `flask.cli.find_best_app()` (used by `flask run`) for runtime
        discovery. This extension uses that discovery order as a reference, but it does not fully
        align with `find_best_app()`.

        Searches in all top-level directories automatically.

        Raises:
            FileNotFoundError: If no valid Flask entrypoint is found
        """
        locations = self._wsgi_locations()
        try:
            return find_entrypoint_with_variable(
                self.project_root, locations, {"app", "application"}
            )
        except FileNotFoundError:
            pass

        try:
            return find_entrypoint_with_factory(
                self.project_root,
                locations,
                factory_names=("create_app", "make_app"),
            )
        except FileNotFoundError:
            raise FileNotFoundError(
                "Missing WSGI entrypoint in default search locations"
            )

    @property
    @override
    def framework(self) -> str:
        """Return the wsgi framework name, e.g. flask, django."""
        return "flask"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:  # noqa: ARG004 (unused arg)
        """Check if the extension is in an experimental state."""
        return False

    @override
    def gen_install_app_part(self) -> dict[str, Any]:
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
                    "main.py",
                    "src",
                    "migrate",
                    "migrate.sh",
                    "migrate.py",
                    "static",
                    "templates",
                )
                if (self.project_root / f).exists()
            ]
        return user_prime

    def _wsgi_locations(self) -> Iterable[Path]:
        """Return the possible locations for the WSGI entrypoint.

        It will look for an `app` global variable in the following places:
        1. `app.py`.
        2. `main.py`.
        3. Inside the directories `app`, `src` and rockcraft name, in the files
           `__init__.py`, `app.py` or `main.py`.
        """
        return (
            Path(".", "app.py"),
            Path(".", "main.py"),
            *(
                Path(src_dir, src_file)
                for src_dir in ("app", "src", self.name)
                for src_file in ("__init__.py", "app.py", "main.py")
            ),
        )

    def _wsgi_path_error_messages(self) -> list[str]:
        """Ensure the extension can infer the WSGI path of the Flask application."""
        try:
            self.wsgi_path  # noqa: B018 (unused expression, just checking for errors)
        except FileNotFoundError:
            return ["Missing WSGI entrypoint in default search locations"]
        except SyntaxError as e:
            filename = Path(e.filename).name if e.filename else "<unknown>"
            return [f"error parsing {filename}: {e.msg}"]
        return []

    def _requirements_error_messages(self) -> list[str]:
        """Ensure the requirements.txt file is correct."""
        requirements_file = self.project_root / "requirements.txt"
        pyproject_file = self.project_root / "pyproject.toml"
        if not requirements_file.exists() and not pyproject_file.exists():
            return [
                "missing a requirements file (requirements.txt or pyproject.toml). The flask-framework extension requires one of these files with 'flask' specified as a dependency."
            ]

        if "flask" not in self._requirements():
            return ["missing flask package dependency in requirements file."]

        return []

    @override
    def check_project(self) -> None:
        """Ensure this extension can apply to the current rockcraft project."""
        error_messages = self._requirements_error_messages()
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
    @override
    def wsgi_path(self) -> str:
        """Return the wsgi path of the wsgi application."""
        module = f"{self.name}.wsgi"
        for wsgi_file in self._wsgi_locations():
            if not wsgi_file.exists():
                continue

            if has_global_variable(wsgi_file, "application"):
                return f"{module}:application"

        raise ExtensionError(
            "django application can not be imported, unable to locate a wsgi.py "
            "with an 'application' callable in the default discovery locations.",
            doc_slug="/reference/extensions/django-framework/#project-requirements",
            logpath_report=False,
        )

    @property
    @override
    def framework(self) -> str:
        """Return the wsgi framework name, e.g. flask, django."""
        return "django"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:  # noqa: ARG004 (unused arg)
        """Check if the extension is in an experimental state."""
        return False

    @override
    def gen_install_app_part(self) -> dict[str, Any]:
        """Return the prime list for the Django project."""
        if "django-framework/install-app" not in self.yaml_data.get("parts", {}):
            return {
                "plugin": "dump",
                "source": self.name,
                "organize": {"*": "django/app/", ".*": "django/app/"},
                "stage": ["-django/app/db.sqlite3"],
            }
        return {}

    def _wsgi_locations(self) -> Iterable[Path]:
        """Return candidate paths for the project's wsgi.py."""
        return (self.project_root / self.name / self.name / "wsgi.py",)

    @override
    def check_project(self) -> None:
        """Ensure this extension can apply to the current rockcraft project."""
        if not (self.project_root / "requirements.txt").exists():
            raise ExtensionError(
                "missing requirements.txt file, django-framework extension "
                "requires this file with Django specified as a dependency",
                doc_slug="/reference/extensions/django-framework/#project-requirements",
                logpath_report=False,
            )
        if not self.yaml_data.get("services", {}).get("django", {}).get("command"):
            self.wsgi_path  # noqa: B018 (unused expression, just checking for errors)
