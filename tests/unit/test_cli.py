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
import pathlib
import sys
from pathlib import Path
from unittest.mock import DEFAULT, call, patch

import pytest
import yaml
from craft_cli import emit
from rockcraft import cli, extensions, services
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
        project_info=DEFAULT,
    )

    package_mocks = mocker.patch.multiple(
        services.RockcraftPackageService, write_metadata=DEFAULT, pack=DEFAULT
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

    assert len(lifecycle_init_mock.mock_calls) == 1
    rendered = lifecycle_init_mock.mock_calls[0].args[0]
    rock_project = project.Project.unmarshal(yaml.safe_load(rendered))
    assert len(rock_project.summary) < 80
    assert len(rock_project.description.split()) < 100
    assert mock_ended_ok.mock_calls == [call()]


def test_run_init_with_name(mocker, lifecycle_init_mock):
    mocker.patch.object(sys, "argv", ["rockcraft", "init", "--name=foobar"])

    cli.run()

    assert len(lifecycle_init_mock.mock_calls) == 1
    rendered = lifecycle_init_mock.mock_calls[0].args[0]
    rock_project = project.Project.unmarshal(yaml.safe_load(rendered))
    assert rock_project.name == "foobar"


def test_run_init_with_invalid_name(mocker, lifecycle_init_mock):
    mocker.patch.object(sys, "argv", ["rockcraft", "init", "--name=f"])
    return_code = cli.run()
    assert return_code == 1


def test_run_init_fallback_name(mocker, lifecycle_init_mock):
    mocker.patch.object(sys, "argv", ["rockcraft", "init"])
    mocker.patch("pathlib.Path.cwd", return_value=pathlib.Path("/f"))

    cli.run()

    rendered = lifecycle_init_mock.mock_calls[0].args[0]
    rock_project = yaml.safe_load(rendered)
    assert rock_project["name"] == "my-rock-name"


def test_run_init_flask(mocker, lifecycle_init_mock, tmp_path, monkeypatch):
    (tmp_path / "requirements.txt").write_text("flask")
    (tmp_path / "app.py").write_text("app = object()")
    mock_ended_ok = mocker.patch.object(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", "init", "--profile=flask-framework"])

    cli.run()

    assert len(lifecycle_init_mock.mock_calls) == 1
    rendered = lifecycle_init_mock.mock_calls[0].args[0]
    rock_project = yaml.safe_load(rendered)
    assert len(rock_project["summary"]) < 80
    assert len(rock_project["description"].split()) < 100
    assert mock_ended_ok.mock_calls == [call()]

    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "0")
    project.Project.unmarshal(extensions.apply_extensions(tmp_path, rock_project))
