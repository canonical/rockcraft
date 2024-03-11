# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021-2024 Canonical Ltd.
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
from pathlib import Path
from unittest.mock import DEFAULT, call, patch

import pytest
import yaml
from craft_cli import emit
from rockcraft import cli, services
from rockcraft.application import Rockcraft
from rockcraft.models import project


@pytest.fixture()
def lifecycle_init_mock():
    """Mock for ui.init."""
    patcher = patch("rockcraft.commands.init.init")
    yield patcher.start()
    patcher.stop()


def test_run_pack_services(mocker, monkeypatch, tmp_path):
    # Pretend it's running inside the managed instance
    monkeypatch.setenv("CRAFT_MANAGED_MODE", "1")

    log_path = tmp_path / "rockcraft.log"
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(Rockcraft, "get_project")
    mocker.patch.object(Rockcraft, "log_path", new=log_path)

    fake_prime_dir = Path("/fake/prime/dir")

    # Mock the relevant methods from the lifecycle and package services
    lifecycle_mocks = mocker.patch.multiple(
        services.RockcraftLifecycleService,
        setup=DEFAULT,
        prime_dir=fake_prime_dir,
        run=DEFAULT,
    )

    package_mocks = mocker.patch.multiple(
        services.RockcraftPackageService,
        write_metadata=DEFAULT,
        pack=DEFAULT,
        update_project=DEFAULT,
    )

    command_line = ["rockcraft", "pack"]
    mocker.patch.object(sys, "argv", command_line)

    cli.run()

    lifecycle_mocks["run"].assert_called_once_with(step_name="prime", part_names=[])

    package_mocks["write_metadata"].assert_called_once_with(fake_prime_dir)
    package_mocks["pack"].assert_called_once_with(fake_prime_dir, Path())

    assert mock_ended_ok.called
    assert log_path.is_file()


def test_run_init(mocker, lifecycle_init_mock):
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", "init"])
    cli.run()

    rock_project = project.Project.unmarshal(
        yaml.safe_load(
            # pylint: disable=W0212
            cli.commands.InitCommand._INIT_TEMPLATE_YAML
        )
    )

    assert len(rock_project.summary) < 80
    assert len(rock_project.description.split()) < 100

    assert lifecycle_init_mock.mock_calls == [
        call(cli.commands.InitCommand._INIT_TEMPLATE_YAML)  # pylint: disable=W0212
    ]
    assert mock_ended_ok.mock_calls == [call()]
