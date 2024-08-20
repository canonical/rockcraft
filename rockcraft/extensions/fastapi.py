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

import ast
import fnmatch
import os
import pathlib
import posixpath
import re
from typing import Any, Dict, Tuple

from overrides import override

from ..errors import ExtensionError
from .extension import Extension


class FastAPIFramework(Extension):
    """An extension base class for Python FastAPI/starlette framework extension."""

    @staticmethod
    @override
    def get_supported_bases() -> Tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu@22.04", "ubuntu:22.04", "ubuntu@24.04"

    @staticmethod
    @override
    def is_experimental(base: str | None) -> bool:
        """Check if the extension is in an experimental state."""
        return True

    @override
    def get_root_snippet(self) -> dict[str, Any]:
        """Return the root snippet to apply."""
        self._check_project()

        snippet: Dict[str, Any] = {
            "run_user": "_daemon_",
            "services": {
                "fastapi": {
                    "override": "replace",
                    "startup": "enabled",
                    "user": "_daemon_",
                    "working-dir": "/app",
                },
            },
        }
        if not self.yaml_data.get("services", {}).get("fastapi", {}).get("command"):
            snippet["services"]["fastapi"][
                "command"
            ] = f"/bin/python3 -m uvicorn {self._asgi_path()}"

        snippet["parts"] = self._gen_parts()
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
    def name(self):
        """Return the normalized name of the rockcraft project."""
        return self.yaml_data["name"].replace("-", "_").lower()

    def has_global_variable(
        self, source_file: pathlib.Path, variable_name: str
    ) -> bool:
        """Check the given Python source code has a global variable defined."""
        # TODO COPY PASTED FROM gunicorn.py. MAYBE EXTRACT IT SOMEWHERE ELSE?
        tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=source_file)
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

    def _gen_parts(self) -> dict:
        """Generate the parts associated with this extension."""
        stage_packages = ["python3-venv"]
        build_environment = []
        if self.yaml_data["base"] == "bare":
            stage_packages = ["python3.12-venv_ensurepip"]
            build_environment = [{"PARTS_PYTHON_INTERPRETER": "python3.12"}]

        # TODO is it worth to try to make _GunicornBase -> _PythonBase?
        parts: Dict[str, Any] = {
            "fastapi-framework/dependencies": {
                "plugin": "python",
                "stage-packages": stage_packages,
                "source": ".",
                "python-packages": ["uvicorn"],
                "python-requirements": ["requirements.txt"],
                "build-environment": build_environment,
            },
            "fastapi-framework/install-app": self._gen_install_app_part(),
        }
        if self.yaml_data["base"] == "bare":
            parts["fastapi-framework/runtime"] = {
                "plugin": "nil",
                "override-build": "mkdir -m 777 ${CRAFT_PART_INSTALL}/tmp",
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
        return parts

    def _gen_install_app_part(self):
        source_files = [f.name for f in sorted(self.project_root.iterdir())]
        # if prime is not in exclude mode, use it to generate the stage and organize
        if self._app_prime and self._app_prime[0] and self._app_prime[0][0] != "-":
            renaming_map = {
                os.path.relpath(file, "app"): file for file in self._app_prime
            }
        else:
            renaming_map = {
                f: posixpath.join("app", f)
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
    def _app_prime(self):
        """Return the prime list for the FastAPI project."""
        user_prime = (
            self.yaml_data.get("parts", {})
            .get("fastapi-framework/install-app", {})
            .get("prime", [])
        )
        if not all(re.match("-? *app/", p) for p in user_prime):
            raise ExtensionError(
                "fastapi-framework extension requires the 'prime' entry in the "
                "fastapi-framework/install-app part to start with app/",
                doc_slug="/reference/extensions/fastapi-framework",
                logpath_report=False,
            )
        if not user_prime:
            user_prime = [
                f"app/{f}"
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
                user_prime.append("app/" + self._find_asgi_location().parts[0])
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
        """TODO returns path (file/directory and the asgi entrypoint in format like app.main:app.

        looks for app.py:app
        looks for app:app (in __init__.py)
        looks for app.app:app
        looks for app.main:app
        looks for src:app (in __init__.py)
        looks for src.app:app
        looks for src.main:app
        looks for PROJECTNAME:app (in __init__.py)
        looks for PROJECTNAME.app:app
        looks for PROJECTNAME.main:app
        """
        places_to_look = (
            (".", "app.py"),
            *(
                (src_dir, src_file)
                for src_dir in ("app", "src", self.name)
                for src_file in ("__init__.py", "app.py", "main.py")
            ),
        )

        for src_dir, src_file in places_to_look:
            full_path = self.project_root / src_dir / src_file
            if full_path.exists():
                if self.has_global_variable(full_path, "app"):
                    return pathlib.Path(src_dir, src_file)

        raise FileNotFoundError("ASGI entrypoint not found")

    def _check_project(self):
        """Ensure this extension can apply to the current rockcraft project."""
        error_messages = self._requirements_txt_error_messages()
        if not self.yaml_data.get("services", {}).get("fastapi", {}).get("command"):
            error_messages += self._asgi_entrypoint_error_messages()
        if error_messages:
            raise ExtensionError(
                "\n".join("- " + message for message in error_messages),
                doc_slug="/reference/extensions/go-framework",
                logpath_report=False,
            )

    def _requirements_txt_error_messages(self) -> list[str]:
        """Ensure the requirements.txt file is correct."""
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
            return ["missing ASGI entrypoint"]
        except SyntaxError as e:
            return [f"Syntax error in  python file in ASGI search path: {e}"]
        return []
