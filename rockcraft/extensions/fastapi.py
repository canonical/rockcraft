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

"""An extension for the FastAPI application extensions."""

import fnmatch
import os
import pathlib
import posixpath
import re
from typing import Any

from overrides import override  # type: ignore[reportUnknownVariableType]

from rockcraft.errors import ExtensionError
from rockcraft.extensions._utils import find_ubuntu_base_python_version
from rockcraft.usernames import SUPPORTED_GLOBAL_USERNAMES

from ._python_utils import has_global_variable
from .app_parts import gen_logging_part
from .extension import Extension

USER_UID: int = SUPPORTED_GLOBAL_USERNAMES["_daemon_"]["uid"]


class FastAPIFramework(Extension):
    """An extension base class for Python FastAPI/starlette framework extension."""

    IMAGE_BASE_DIR = "app"

    @staticmethod
    @override
    def get_supported_bases() -> tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@24.04"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:  # noqa: ARG004 (unused arg)
        """Check if the extension is in an experimental state."""
        return True

    @override
    def get_root_snippet(self) -> dict[str, Any]:
        """Return the root snippet to apply."""
        self._check_project()

        snippet: dict[str, Any] = {
            "run_user": "_daemon_",
            "services": {
                "fastapi": {
                    "override": "replace",
                    "startup": "enabled",
                    "user": "_daemon_",
                    "working-dir": f"/{self.IMAGE_BASE_DIR}",
                    "environment": {
                        # not listening on all interfaces complicates exposing ports outside of the
                        # container and the user would have to create this environment variable manually.
                        "UVICORN_HOST": "0.0.0.0",  # noqa: S104
                    },
                },
            },
        }
        if not self.yaml_data.get("services", {}).get("fastapi", {}).get("command"):
            snippet["services"]["fastapi"]["command"] = (
                f"/bin/python3 -m uvicorn {self._asgi_path()}"
            )

        snippet["parts"] = self._get_parts()
        return snippet

    @override
    def get_parts_snippet(self) -> dict[str, Any]:
        """Return the parts to add to parts."""
        return {}

    @override
    def get_part_snippet(self) -> dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}

    @property
    def name(self) -> str:
        """Return the normalized name of the rockcraft project."""
        return self.yaml_data["name"].replace("-", "_").lower()

    def _get_parts(self) -> dict[str, Any]:
        """Generate the parts associated with this extension."""
        stage_packages = ["python3-venv"]
        build_environment = []
        if self.yaml_data["base"] == "bare":
            try:
                python_version = find_ubuntu_base_python_version(
                    base=self.yaml_data["build-base"]
                )
            except NotImplementedError:
                raise ExtensionError(
                    f"Unable to determine the Python version for the build-base {self.yaml_data['build-base']}",
                    doc_slug="/reference/extensions/fastapi",
                    logpath_report=False,
                )
            stage_packages = [f"python{python_version}-venv_ensurepip"]
            build_environment = [
                {"PARTS_PYTHON_INTERPRETER": f"python{python_version}"}
            ]

        parts: dict[str, Any] = {
            "fastapi-framework/dependencies": {
                "plugin": "python",
                "stage-packages": stage_packages,
                "source": ".",
                "python-packages": ["uvicorn"],
                "python-requirements": ["requirements.txt"],
                "build-environment": build_environment,
            },
            "fastapi-framework/install-app": {
                **self._get_install_app_part(),
                "permissions": [{"owner": USER_UID, "group": USER_UID}],
            },
        }
        if self.yaml_data["base"] == "bare":
            parts["fastapi-framework/runtime"] = {
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
            parts["fastapi-framework/runtime"] = {
                "plugin": "nil",
                "stage-packages": ["ca-certificates_data"],
            }
        parts["fastapi-framework/logging"] = gen_logging_part()
        return parts

    def _get_install_app_part(self) -> dict[str, Any]:
        source_files = [f.name for f in sorted(self.project_root.iterdir())]
        # if prime is not in exclude mode, use it to generate the stage and organize
        if self._app_prime and self._app_prime[0] and self._app_prime[0][0] != "-":
            renaming_map = {
                os.path.relpath(file, self.IMAGE_BASE_DIR): file
                for file in self._app_prime
            }
        else:
            renaming_map = {
                f: posixpath.join(self.IMAGE_BASE_DIR, f)
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
        }

    @property
    def _app_prime(self) -> list[str]:
        """Return the prime list for the FastAPI project."""
        user_prime = (
            self.yaml_data.get("parts", {})
            .get("fastapi-framework/install-app", {})
            .get("prime", [])
        )
        if not all(re.match(f"-? *{self.IMAGE_BASE_DIR}/", p) for p in user_prime):
            raise ExtensionError(
                "fastapi-framework extension requires the 'prime' entry in the "
                f"fastapi-framework/install-app part to start with {self.IMAGE_BASE_DIR}/",
                doc_slug="/reference/extensions/fastapi-framework",
                logpath_report=False,
            )
        if not user_prime:
            user_prime = [
                f"{self.IMAGE_BASE_DIR}/{f}"
                for f in (
                    "migrate",
                    "migrate.sh",
                    "migrate.py",
                    "static",
                    "templates",
                )
                if (self.project_root / f).exists()
            ]
            if not self.yaml_data.get("services", {}).get("fastapi", {}).get("command"):
                user_prime.append(
                    f"{self.IMAGE_BASE_DIR}/" + self._find_asgi_location().parts[0]
                )
        return user_prime

    def _asgi_path(self) -> str:
        asgi_location = self._find_asgi_location()
        return (
            ".".join(
                part.removesuffix(".py")
                for part in asgi_location.parts
                if part != "__init__.py"
            )
            + ":app"
        )

    def _find_asgi_location(self) -> pathlib.Path:
        """Return the path of the asgi entrypoint file.

        It will look for an `app` global variable in the following places:
        1. `app.py`.
        2. Inside the directories `app`, `src` and rockcraft name, in the files
           `__init__.py`, `app.py` or `main.py`.

        It will return the first instance found or raise FileNotFoundError.
        """
        places_to_look = (
            (".", "app.py"),
            (".", "main.py"),
            *(
                (src_dir, src_file)
                for src_dir in ("app", "src", self.name)
                for src_file in ("__init__.py", "app.py", "main.py")
            ),
        )

        for src_dir, src_file in places_to_look:
            full_path = self.project_root / src_dir / src_file
            if full_path.exists() and has_global_variable(full_path, "app"):
                return pathlib.Path(src_dir, src_file)

        raise FileNotFoundError("ASGI entrypoint not found")

    def _check_project(self) -> None:
        """Ensure this extension can apply to the current rockcraft project."""
        error_messages = self._requirements_txt_error_messages()
        if not self.yaml_data.get("services", {}).get("fastapi", {}).get("command"):
            error_messages += self._asgi_entrypoint_error_messages()
        if error_messages:
            raise ExtensionError(
                "\n".join("- " + message for message in error_messages),
                doc_slug="/reference/extensions/fastapi-framework/#project-requirements",
                logpath_report=False,
            )

    def _requirements_txt_error_messages(self) -> list[str]:
        """Ensure the requirements.txt file exists and has fastapi or starlette deps."""
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            return [
                "missing a requirements.txt file. The fastapi-framework extension requires this file with 'fastapi'/'starlette' specified as a dependency."
            ]

        requirements_lines = requirements_file.read_text(encoding="utf-8").splitlines()
        if not any(
            dep in line.lower()
            for line in requirements_lines
            for dep in ("fastapi", "starlette")
        ):
            return [
                "missing fastapi or starlette package dependency in requirements.txt file."
            ]

        return []

    def _asgi_entrypoint_error_messages(self) -> list[str]:
        try:
            self._find_asgi_location()
        except FileNotFoundError:
            return [
                (
                    "missing ASGI entrypoint\n"
                    "  Cannot find 'app' global variable in the following places:\n"
                    "  1. app.py.\n"
                    "  2. In files __init__.py, and main.py in the 'app',"
                    "'src', and root project directories."
                ),
            ]
        except SyntaxError as e:
            return [f"Syntax error in  python file in ASGI search path: {e}"]
        return []
