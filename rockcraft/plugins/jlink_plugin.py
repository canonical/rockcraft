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

"""The Java runtime plugin."""

from typing import Dict, List, Literal, Set, cast

from craft_parts.plugins import Plugin, PluginProperties
from overrides import override


class JLinkPluginProperties(PluginProperties, frozen=True):
    """The part properties used by the JLink plugin."""

    plugin: Literal["jlink"] = "jlink"
    jlink_java_version: int = 21
    jlink_jars: list[str] = []
    jlink_dep_slices: list[str] = []


class JLinkPlugin(Plugin):
    """Create a Java Runtime using JLink."""

    properties_class = JLinkPluginProperties

    @override
    def get_build_packages(self) -> Set[str]:
        options = cast(JLinkPluginProperties, self._options)
        return {f"openjdk-{options.jlink_java_version}-jdk"}

    @override
    def get_build_environment(self) -> Dict[str, str]:
        return {}

    @override
    def get_build_snaps(self) -> Set[str]:
        return {}

    @override
    def get_build_commands(self) -> List[str]:
        """Return a list of commands to run during the build step."""
        options = cast(JLinkPluginProperties, self._options)

        commands = []
        slices = " ".join(options.jlink_dep_slices)
        if len(slices) == 0:
            slices = f"base-files_base openjdk-{options.jlink_java_version}-jre-headless_core"

        if hasattr(options, "source") and isinstance(options.source, str):
            commands.append(
                "chisel cut --release ./ --root ${CRAFT_PART_INSTALL} " + slices
            )
        else:
            commands.append("chisel cut --root ${CRAFT_PART_INSTALL} " + slices)

        if len(options.jlink_jars) > 0:
            jars = " ".join(["${CRAFT_STAGE}/" + x for x in options.jlink_jars])
            commands.append(f"PROCESS_JARS={jars}")
        else:
            commands.append("PROCESS_JARS=$(find ${CRAFT_STAGE} -type f -name *.jar)")

        # create temp folder
        commands.append("mkdir -p ${CRAFT_PART_BUILD}/tmp")
        # extract jar files into temp folder
        commands.append(
            "(cd ${CRAFT_PART_BUILD}/tmp && for jar in ${PROCESS_JARS}; do jar xvf ${jar}; done;)"
        )
        commands.append("cpath=$(find ${CRAFT_PART_BUILD}/tmp -type f -name *.jar)")
        commands.append("cpath=$(echo ${cpath} | sed s'/[[:space:]]/:/'g)")
        commands.append("echo ${cpath}")
        commands.append(
            'if [ "x${PROCESS_JARS}" != "x" ]; then deps=$(jdeps --class-path=${cpath} -q --recursive  --ignore-missing-deps --print-module-deps --multi-release 21 ${PROCESS_JARS}); else deps=java.base; fi'
        )
        commands.append(
            "install_root=${CRAFT_PART_INSTALL}/usr/lib/jvm/java-21-openjdk-${CRAFT_TARGET_ARCH}/"
        )

        commands.append(
            "rm -rf ${install_root} && jlink --add-modules ${deps} --output ${install_root}"
        )
        # create /usr/bin/java link
        commands.append(
            "(cd ${CRAFT_PART_INSTALL} && mkdir -p usr/bin && ln -s --relative usr/lib/jvm/java-21-openjdk-${CRAFT_TARGET_ARCH}/bin/java usr/bin/)"
        )
        commands.append("mkdir -p ${CRAFT_PART_INSTALL}/etc/ssl/certs/java/")
        # link cacerts
        commands.append(
            "cp /etc/ssl/certs/java/cacerts ${CRAFT_PART_INSTALL}/etc/ssl/certs/java/cacerts"
        )
        commands.append("cd ${CRAFT_PART_INSTALL}")
        commands.append(
            "rm -f usr/lib/jvm/java-21-openjdk-${CRAFT_TARGET_ARCH}/lib/security/cacerts"
        )
        commands.append(
            "ln -s --relative etc/ssl/certs/java/cacerts usr/lib/jvm/java-21-openjdk-${CRAFT_TARGET_ARCH}/lib/security/cacerts"
        )
        return commands
