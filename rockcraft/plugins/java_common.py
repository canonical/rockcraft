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
"""Common functionality for Java-based plugins.

This module provides a function to create a /usr/bin/java symlink.
"""


def create_usr_bin_java() -> list[str]:
    """Get the bash commands to create /usr/bin/java symlink."""
    return [
        '# Find the "java" executable and make a link to it in $CRAFT_PART_INSTALL/bin/java',
        "java_bin=$(find ${CRAFT_PART_INSTALL} -name java -type f -executable)",
        "test -d ${CRAFT_PART_INSTALL}/usr/bin && "
        "(test -f ${CRAFT_PART_INSTALL}/usr/bin/java || "
        "ln -s --relative $java_bin ${CRAFT_PART_INSTALL}/usr/bin/java)",
    ]
