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

"""Utils for Python based extensions."""

import ast
from pathlib import Path
from typing import Iterable


def find_file_with_variable(
    base_dir: Path, python_paths: Iterable[Path], variable_name: str
) -> Path:
    """Find Python file that contains a given global variable.

    Given a base_dir, several paths for Python files, and a variable_name, return the first
    path that contains variable_name as a global variable. If the variable is not found,
    raise FileNotFoundError.
    """
    for python_path in python_paths:
        full_path = base_dir / python_path
        if full_path.exists() and has_global_variable(full_path, variable_name):
            return python_path
    raise FileNotFoundError(f"File not found with variable {variable_name}")


def find_entrypoint_with_variable(
    base_dir: Path, python_paths: Iterable[Path], variable_name: str
) -> str:
    """Find Python file entrypoint for a global variable.

    Given a base_dir, several paths for Python files, and a variable_name, return the first
    entrypoing that contains variable_name as a global variable in the format path:variable_name,
    following ASGI and WSGI specification. If the variable is not found, raise FileNotFoundError.
    """
    python_path = find_file_with_variable(base_dir, python_paths, variable_name)
    return (
        ".".join(
            part.removesuffix(".py")
            for part in python_path.parts
            if part != "__init__.py"
        )
        + f":{variable_name}"
    )


def has_global_variable(source_file: Path, variable_name: str) -> bool:
    """Check whether the given Python source code has a global variable defined."""
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
