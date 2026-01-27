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
from collections.abc import Iterable
from pathlib import Path


def find_file_with_variable(
    base_dir: Path, python_paths: Iterable[Path], variable_names: Iterable[str]
) -> tuple[Path, str]:
    """Find Python file that contains any of the variable_names as a global variable.

    Given a base_dir, several paths for Python files, and variable_names, return the path
    to the first file that contains variable_name as a global variable.
    If not found, raise FileNotFoundError.
    """
    for python_path in python_paths:
        full_path = base_dir / python_path
        if not full_path.exists():
            continue

        for variable_name in variable_names:
            if has_global_variable(full_path, variable_name):
                return python_path, variable_name

    raise FileNotFoundError(
        f"File not found with variables: {', '.join(variable_names)}"
    )


def find_file_with_factory(
    base_dir: Path, python_paths: Iterable[Path], factory_names: Iterable[str]
) -> tuple[Path, str]:
    """Find Python file that contains a factory function.

    Looks for application factory functions like create_app or make_app,
    matching Flask's discovery behavior.

    Given a base_dir and several paths for Python files, return a tuple of
    (path, factory_name) where factory_name is the factory function name found.
    If not found, raise FileNotFoundError.
    """
    for python_path in python_paths:
        full_path = base_dir / python_path
        if not full_path.exists():
            continue

        factory_name = has_factory_function(full_path, factory_names)
        if factory_name:
            return python_path, factory_name

    raise FileNotFoundError("File not found with factory functions ")


def find_entrypoint_with_variable(
    base_dir: Path, python_paths: Iterable[Path], variable_names: Iterable[str]
) -> str:
    """Find Python file entrypoint for a global variable.

    Returns WSGI format: "module:app"

    Given a base_dir, several paths for Python files, and a variable_name, return the first
    entrypoint that contains variable_name as a global variable,
    following ASGI and WSGI specification. If not found, raise FileNotFoundError.
    """
    python_path, variable_name = find_file_with_variable(
        base_dir, python_paths, variable_names
    )
    module_path = ".".join(
        part.removesuffix(".py") for part in python_path.parts if part != "__init__.py"
    )
    return f"{module_path}:{variable_name}"


def find_entrypoint_with_factory(
    base_dir: Path, python_paths: Iterable[Path], factory_names: Iterable[str]
) -> str:
    """Find Python file entrypoint for a factory function.

    Returns WSGI format: "module:create_app()" or "module:make_app()"

    Given a base_dir and several paths for Python files, return the first
    entrypoint that contains a factory function (create_app or make_app),
    following ASGI and WSGI specification. If not found, raise FileNotFoundError.
    """
    python_path, factory_name = find_file_with_factory(
        base_dir, python_paths, factory_names
    )
    module_path = ".".join(
        part.removesuffix(".py") for part in python_path.parts if part != "__init__.py"
    )
    return f"{module_path}:{factory_name}()"


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


def has_factory_function(source_file: Path, factory_names: Iterable[str]) -> str | None:
    """Check whether the given Python source code has a factory function defined.

    Looks for application factory functions from the provided list.

    Args:
        source_file: Path to the Python source file to check
        factory_names: Iterable of factory function names to search for

    Returns:
        The name of the first factory function found, or None if not found.
        Checks in the order provided in factory_names.

    """
    tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=source_file)
    for factory_name in factory_names:
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef) and node.name == factory_name:
                return factory_name
    return None
