# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021-2022 Canonical Ltd.
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

import sys
from unittest.mock import call, patch

import pytest
import yaml
from craft_cli import emit

from rockcraft import cli, project


@pytest.fixture
def lifecycle_pack_mock():
    """Mock for ui.pack."""
    patcher = patch("rockcraft.lifecycle.pack")
    yield patcher.start()
    patcher.stop()


@pytest.fixture
def lifecycle_init_mock():
    """Mock for ui.init."""
    patcher = patch("rockcraft.lifecycle.init")
    yield patcher.start()
    patcher.stop()


def test_run_defaults(mocker, lifecycle_pack_mock):
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", "pack"])
    cli.run()

    assert lifecycle_pack_mock.mock_calls == [call()]
    assert mock_ended_ok.mock_calls == [call()]


def test_run_init(mocker, lifecycle_init_mock):
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", "init"])
    cli.run()

    rock_project = project.Project.unmarshal(
        yaml.safe_load(cli.commands.InitCommand._INIT_TEMPLATE_YAML)
    )

    assert len(rock_project.summary) < 80
    assert len(rock_project.description.split()) < 100

    assert lifecycle_init_mock.mock_calls == [
        call(cli.commands.InitCommand._INIT_TEMPLATE_YAML)
    ]
    assert mock_ended_ok.mock_calls == [call()]
