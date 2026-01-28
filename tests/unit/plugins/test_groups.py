# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2026 Canonical Ltd.
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

"""Tests for base-specific plugin groups for Rockcraft."""

import pytest
from craft_parts.plugins.dotnet_plugin import DotnetPlugin as DotnetPluginV1
from craft_parts.plugins.python_v2.python_plugin import PythonPlugin as PythonPluginV2
from rockcraft.plugins.groups import get_plugin_group
from rockcraft.plugins.poetry_plugin import PoetryPlugin as PoetryPluginV1
from rockcraft.plugins.python_plugin import PythonPlugin as PythonPluginV1
from rockcraft.plugins.uv_plugin import UvPlugin as UvPluginV1

LEGACY_BASES = ["ubuntu@20.04", "ubuntu@22.04", "ubuntu@24.04"]
DEFAULT_BASES = ["ubuntu@25.10", "devel", "ubuntu@devel"]


@pytest.mark.parametrize("legacy_base", LEGACY_BASES)
def test_legacy_groups_dotnet(legacy_base):
    group = get_plugin_group(legacy_base)
    assert group["dotnet"] is DotnetPluginV1


@pytest.mark.parametrize("base", DEFAULT_BASES)
def test_default_dotnet(base):
    group = get_plugin_group(base)
    assert "dotnet" not in group


@pytest.mark.parametrize("legacy_base", LEGACY_BASES)
def test_legacy_groups_python(legacy_base):
    group = get_plugin_group(legacy_base)
    assert group["python"] is PythonPluginV1
    assert group["poetry"] is PoetryPluginV1
    assert group["uv"] is UvPluginV1


@pytest.mark.parametrize("base", DEFAULT_BASES)
def test_default_python(base):
    group = get_plugin_group(base)
    assert group["python"] is PythonPluginV2
    # No v2 of the poetry and uv plugins yet
    assert "poetry" not in group
    assert "uv" not in group
