# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
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
from craft_application.commands.lifecycle import PackCommand


def test_application_commands(default_application):
    commands = default_application.command_groups

    assert len(commands) == 1

    group = commands[0]
    assert group.name == "Lifecycle"

    # Only the Pack command is supported currently.
    assert len(group.commands) == 1
    assert group.commands[0] is PackCommand
