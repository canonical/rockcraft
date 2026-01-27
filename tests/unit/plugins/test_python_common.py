# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2025 Canonical Ltd.
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
import pytest
from craft_parts.plugins.python_v2.python_plugin import PythonPlugin as PythonPluginV2
from rockcraft.plugins import python_common
from rockcraft.plugins.poetry_plugin import PoetryPlugin as PoetryPluginV1
from rockcraft.plugins.python_plugin import PythonPlugin as PythonPluginV1
from rockcraft.plugins.uv_plugin import UvPlugin as UvPluginV1


@pytest.mark.parametrize("base", ["ubuntu@20.04", "ubuntu@22.04", "ubuntu@24.04", None])
def test_get_python_plugins_v1(base):
    plugins = python_common.get_python_plugins(base)

    assert plugins["python"] is PythonPluginV1
    assert plugins["uv"] is UvPluginV1
    assert plugins["poetry"] is PoetryPluginV1


@pytest.mark.parametrize("base", ["ubuntu@25.10", "devel"])
def test_get_python_plugins_v2(base):
    plugins = python_common.get_python_plugins(base)

    assert plugins["python"] is PythonPluginV2
    # No "V2" versions for uv and poetry yet
    assert "uv" not in plugins
    assert "poetry" not in plugins
