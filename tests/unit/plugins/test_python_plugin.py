# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
# pylint: disable=protected-access

import typing
from pathlib import Path

import pytest
from craft_parts import Part, PartInfo, ProjectInfo
from rockcraft.models.project import Project
from rockcraft.plugins import PythonPlugin

from tests.util import ubuntu_only

pytestmark = ubuntu_only

# Extract the possible "base" values from the Literal annotation.
ALL_BASES = typing.get_args(typing.get_type_hints(Project)["base"])


def create_plugin(base: str, cache_dir: Path) -> PythonPlugin:
    part_info = PartInfo(
        project_info=ProjectInfo(
            application_name="test",
            project_name="test-rock",
            base=base,
            cache_dir=cache_dir,
        ),
        part=Part("my-part", {}),
    )
    properties = PythonPlugin.properties_class.unmarshal({"source": "."})
    return PythonPlugin(properties=properties, part_info=part_info)


@pytest.mark.parametrize("base", ALL_BASES)
def test_invariants(base, tmp_path):
    plugin = create_plugin(base, tmp_path)

    assert plugin._get_system_python_interpreter() is None
    assert plugin._get_script_interpreter() == "#!/bin/${PARTS_PYTHON_INTERPRETER}"


@pytest.mark.parametrize("base", ALL_BASES)
def test_should_remove_symlinks(base, tmp_path):
    plugin = create_plugin(base, tmp_path)

    if base == "bare":
        assert not plugin._should_remove_symlinks()
    else:
        assert plugin._should_remove_symlinks()
