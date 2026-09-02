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
from craft_parts import Part, PartInfo, ProjectInfo
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


def test_get_python_plugins_v2_2604():
    plugins = python_common.get_python_plugins("ubuntu@26.04")

    assert plugins["python"] is PythonPluginV2
    assert plugins["uv"] is UvPluginV1
    assert "poetry" not in plugins


@pytest.mark.parametrize(
    ("base", "interpreter"),
    [("ubuntu@24.04", "python3"), ("ubuntu@26.04", "python3.14")],
)
def test_uv_system_python_interpreter(mocker, base, interpreter):
    plugin = mocker.Mock()
    plugin._part_info.project_info.build_base = base

    assert UvPluginV1._get_system_python_interpreter(plugin) == interpreter


@pytest.mark.parametrize(
    ("build_base", "interpreter"),
    [("ubuntu@24.04", "python3"), ("ubuntu@26.04", "python3.14")],
)
def test_uv_build_environment(tmp_path, build_base, interpreter):
    part_info = PartInfo(
        project_info=ProjectInfo(
            application_name="test",
            project_name="test-rock",
            base="bare",
            build_base=build_base,
            cache_dir=tmp_path,
        ),
        part=Part("my-part", {}),
    )
    properties = UvPluginV1.properties_class.unmarshal({"source": "."})
    plugin = UvPluginV1(properties=properties, part_info=part_info)

    environment = plugin.get_build_environment()
    assert environment["PARTS_PYTHON_INTERPRETER"] == interpreter


@pytest.mark.parametrize("base", ["bare", "ubuntu@26.04"])
def test_uv_2604_build_commands(tmp_path, base):
    part_info = PartInfo(
        project_info=ProjectInfo(
            application_name="test",
            project_name="test-rock",
            base=base,
            build_base="ubuntu@26.04",
            cache_dir=tmp_path,
        ),
        part=Part("my-part", {}),
    )
    properties = UvPluginV1.properties_class.unmarshal({"source": "."})
    plugin = UvPluginV1(properties=properties, part_info=part_info)

    commands = plugin.get_build_commands()
    install_dir = part_info.part_install_dir

    venv_dir = install_dir / ".venv"
    assert commands[1] == (
        f'uv venv --relocatable --allow-existing --python python3.14 "{venv_dir}"'
    )
    merge_command = next(command for command in commands if command.startswith("cp -a"))
    assert (
        f'cp -a "{venv_dir}/bin/." "{install_dir}/usr/bin/"\n'
        f'cp -a "{venv_dir}/lib/." "{install_dir}/usr/lib/"\n' in merge_command
    )
    assert (
        f'mv "{venv_dir}/pyvenv.cfg" "{install_dir}/pyvenv.cfg"\n'
        f'rm -rf "{venv_dir}"' in merge_command
    )
    assert f'rm "{venv_dir}"/bin/python*' in commands

    aliases = (
        f'ln -sf python3.14 "{install_dir}/usr/bin/python3"\n'
        f'ln -sf python3 "{install_dir}/usr/bin/python"\n'
    )
    if base == "bare":
        assert aliases in merge_command
    else:
        assert aliases not in merge_command
