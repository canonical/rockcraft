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
import argparse
from textwrap import dedent

import pytest

from rockcraft import extensions
from rockcraft.commands import ExtensionsCommand, ListExtensionsCommand
from tests.unit.testing.extensions import ExperimentalExtension, FakeExtension


@pytest.fixture()
def setup_extensions(mock_extensions):
    extensions.register(FakeExtension.NAME, FakeExtension)
    extensions.register(ExperimentalExtension.NAME, ExperimentalExtension)


@pytest.mark.parametrize("command_class", [ListExtensionsCommand, ExtensionsCommand])
def test_list_extensions(setup_extensions, emitter, command_class):
    command = command_class(None)
    command.run(argparse.Namespace())
    emitter.assert_message(
        dedent(
            """\
        Extension name          Supported bases
        ----------------------  --------------------------
        experimental-extension  ubuntu@20.04, ubuntu@22.04
        fake-extension          ubuntu@22.04"""
        )
    )
