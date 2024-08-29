# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2024 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path

import pytest
from craft_parts.infos import PartInfo, ProjectInfo
from craft_parts.parts import Part
from rockcraft.plugins.jlink_plugin import JLinkPlugin


@pytest.fixture()
def setup_method_fixture():
    def _setup_method_fixture(new_dir, properties=None):
        if properties is None:
            properties = {}
        plugin_properties = JLinkPlugin.properties_class.unmarshal(properties)
        part = Part("foo", {})

        project_info = ProjectInfo(application_name="test", cache_dir=new_dir)
        project_info._parallel_build_count = 42

        part_info = PartInfo(project_info=project_info, part=part)
        part_info._part_install_dir = Path("install/dir")

        return JLinkPlugin(properties=plugin_properties, part_info=part_info)

    return _setup_method_fixture


class TestPluginJLinkPlugin:
    """JLink plugin tests."""

    def test_get_build_snaps(self, setup_method_fixture, new_dir):
        plugin = setup_method_fixture(new_dir)
        assert plugin.get_build_snaps() == set()

    def test_get_build_packages_default(self, setup_method_fixture, new_dir):
        plugin = setup_method_fixture(new_dir)
        assert plugin.get_build_packages() == {"openjdk-21-jdk"}

    def test_get_build_packages_17(self, setup_method_fixture, new_dir):
        plugin = setup_method_fixture(new_dir, properties={"jlink-java-version": "17"})
        assert plugin.get_build_packages() == {"openjdk-17-jdk"}

    def test_get_build_environment(self, setup_method_fixture, new_dir):
        plugin = setup_method_fixture(new_dir)

        assert plugin.get_build_environment() == {}

    def test_get_build_commands_default(self, setup_method_fixture, new_dir):
        plugin = setup_method_fixture(new_dir)

        commands = plugin.get_build_commands()
        assert (
            "chisel cut --root ${CRAFT_PART_INSTALL} base-files_base openjdk-21-jre-headless_core"
            in commands
        )
        assert "PROCESS_JARS=$(find ${CRAFT_STAGE} -type f -name *.jar)" in commands

    def test_get_build_commands_17(self, setup_method_fixture, new_dir):
        plugin = setup_method_fixture(new_dir, properties={"jlink-java-version": "17"})

        commands = plugin.get_build_commands()
        assert (
            "chisel cut --root ${CRAFT_PART_INSTALL} base-files_base openjdk-17-jre-headless_core"
            in commands
        )

    def test_get_build_commands_chisel_source(self, setup_method_fixture, new_dir):
        plugin = setup_method_fixture(new_dir, properties={"source": "foo"})

        commands = plugin.get_build_commands()
        assert (
            "chisel cut --release ./ --root ${CRAFT_PART_INSTALL} base-files_base openjdk-21-jre-headless_core"
            in commands
        )
        assert "PROCESS_JARS=$(find ${CRAFT_STAGE} -type f -name *.jar)" in commands

    def test_get_build_commands_jars(self, setup_method_fixture, new_dir):
        plugin = setup_method_fixture(new_dir, properties={"jlink-jars": ["foo.jar"]})
        assert "PROCESS_JARS=${CRAFT_STAGE}/foo.jar" in plugin.get_build_commands()

    def test_get_build_commands_deps(self, setup_method_fixture, new_dir):
        plugin = setup_method_fixture(
            new_dir, properties={"jlink-dep-slices": ["base-files_base"]}
        )
        commands = plugin.get_build_commands()
        assert "chisel cut --root ${CRAFT_PART_INSTALL} base-files_base" in commands
