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
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TypeAlias

MatchFn: TypeAlias = Callable[[Path], str | None]


def _find_python_file(
    base_dir: Path,
    python_paths: Iterable[Path],
    match_fn: MatchFn,
    not_found_message: str,
) -> tuple[Path, str]:
    """Find a Python file matching a condition.

    Args:
        base_dir: Base directory to resolve the Python paths.
        python_paths: Iterable of candidate Python file paths.
        match_fn: Function that takes a source file path and returns a match string if it matches
            the condition, or None if it doesn't match.
        not_found_message: Error message to include in the FileNotFoundError if no match is found.

    Returns:
        A tuple of (path, match_string) for the first match.

    """
    for python_path in python_paths:
        full_path = base_dir / python_path
        if not full_path.exists():
            continue

        match = match_fn(full_path)
        if match:
            return python_path, match

    raise FileNotFoundError(not_found_message)


def _build_module_path(python_path: Path) -> str:
    """Convert a python path into the importable module dotted path."""
    return ".".join(
        part.removesuffix(".py") for part in python_path.parts if part != "__init__.py"
    )


def has_global_variable(source_file: Path, variable_name: str) -> bool:
    """Check whether a Python source file defines a global variable."""
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


def _match_variable_in_file(
    source_file: Path, variable_names: Iterable[str]
) -> str | None:
    """Return the first variable defined in the file from the provided list."""
    for variable_name in variable_names:
        if has_global_variable(source_file, variable_name):
            return variable_name
    return None


def find_file_with_variable(
    base_dir: Path, python_paths: Iterable[Path], variable_names: Iterable[str]
) -> tuple[Path, str]:
    """Find a Python file that defines one of the given global variables.

    Args:
        base_dir: Base directory to resolve the Python paths.
        python_paths: Iterable of candidate Python file paths.
        variable_names: Iterable of global variable names to search for.

    Returns:
        A tuple of (path, variable_name) for the first match.

    Raises:
        FileNotFoundError: If no file contains any of the variables.

    """
    return _find_python_file(
        base_dir,
        python_paths,
        lambda source_file: _match_variable_in_file(source_file, variable_names),
        f"File not found with variables: {', '.join(variable_names)}",
    )


def find_entrypoint_with_variable(
    base_dir: Path, python_paths: Iterable[Path], variable_names: Iterable[str]
) -> str:
    """Find a WSGI entrypoint for a global variable."""
    python_path, variable_name = find_file_with_variable(
        base_dir, python_paths, variable_names
    )
    module_path = _build_module_path(python_path)
    return f"{module_path}:{variable_name}"


def _match_factory_in_file(
    source_file: Path, factory_names: Iterable[str]
) -> str | None:
    """Return the first factory function defined in the file from the list."""
    tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=source_file)
    for factory_name in factory_names:
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef) and node.name == factory_name:
                return factory_name
    return None


def find_file_with_factory(
    base_dir: Path, python_paths: Iterable[Path], factory_names: Iterable[str]
) -> tuple[Path, str]:
    """Find a Python file that defines an application factory function.

    Looks for application factory functions like create_app or make_app,
    matching Flask's discovery behavior.

    Args:
        base_dir: Base directory to resolve the Python paths.
        python_paths: Iterable of candidate Python file paths.
        factory_names: Iterable of factory function names to search for.

    Returns:
        A tuple of (path, factory_name) for the first match.

    Raises:
        FileNotFoundError: If no file contains any of the factory functions.

    """
    return _find_python_file(
        base_dir,
        python_paths,
        lambda source_file: _match_factory_in_file(source_file, factory_names),
        "File not found with factory functions",
    )


def find_entrypoint_with_factory(
    base_dir: Path, python_paths: Iterable[Path], factory_names: Iterable[str]
) -> str:
    """Find a WSGI entrypoint for a factory function.

    Returns a WSGI entrypoint in the format "module:factory()".

    Args:
        base_dir: Base directory to resolve the Python paths.
        python_paths: Iterable of candidate Python file paths.
        factory_names: Iterable of factory function names to search for.

    Returns:
        The first matching WSGI entrypoint.

    Raises:
        FileNotFoundError: If no file contains any of the factory functions.

    """
    python_path, factory_name = find_file_with_factory(
        base_dir, python_paths, factory_names
    )
    module_path = _build_module_path(python_path)
    return f"{module_path}:{factory_name}()"
