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
import pathlib


def has_global_variable(source_file: pathlib.Path, variable_name: str) -> bool:
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
