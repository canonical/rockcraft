# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2021 Canonical Ltd
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

from pathlib import Path
from unittest.mock import call

import pytest

from rockcraft import errors, utils


@pytest.fixture
def mock_isatty(mocker):
    yield mocker.patch("rockcraft.utils.sys.stdin.isatty", return_value=True)


@pytest.fixture
def mock_input(mocker):
    yield mocker.patch("rockcraft.utils.input", return_value="")


@pytest.fixture
def mock_is_managed_mode(mocker):
    yield mocker.patch("rockcraft.utils.is_managed_mode", return_value=False)


@pytest.fixture
def mock_which(mocker):
    return mocker.patch("shutil.which")


def test_get_managed_environment_home_path():
    dirpath = utils.get_managed_environment_home_path()

    assert dirpath == Path("/root")


def test_get_managed_environment_project_path():
    dirpath = utils.get_managed_environment_project_path()

    assert dirpath == Path("/root/project")


def test_get_managed_environment_snap_channel(monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_INSTALL_SNAP_CHANNEL", "latest/edge")

    assert utils.get_managed_environment_snap_channel() == "latest/edge"


def test_get_managed_environment_snap_channel_none(monkeypatch):
    monkeypatch.delenv("ROCKCRAFT_INSTALL_SNAP_CHANNEL", raising=False)

    assert utils.get_managed_environment_snap_channel() is None


def test_confirm_with_user_defaults_with_tty(mock_input, mock_isatty):
    mock_input.return_value = ""
    mock_isatty.return_value = True

    assert utils.confirm_with_user("prompt", default=True) is True
    assert mock_input.mock_calls == [call("prompt [Y/n]: ")]
    mock_input.reset_mock()

    assert utils.confirm_with_user("prompt", default=False) is False
    assert mock_input.mock_calls == [call("prompt [y/N]: ")]


def test_confirm_with_user_defaults_without_tty(mock_input, mock_isatty):
    mock_isatty.return_value = False

    assert utils.confirm_with_user("prompt", default=True) is True
    assert utils.confirm_with_user("prompt", default=False) is False

    assert mock_input.mock_calls == []


@pytest.mark.parametrize(
    "user_input,expected",
    [
        ("y", True),
        ("Y", True),
        ("yes", True),
        ("YES", True),
        ("n", False),
        ("N", False),
        ("no", False),
        ("NO", False),
    ],
)
def test_confirm_with_user(user_input, expected, mock_input, mock_isatty):
    mock_input.return_value = user_input

    assert utils.confirm_with_user("prompt") == expected
    assert mock_input.mock_calls == [call("prompt [y/N]: ")]


def test_confirm_with_user_errors_in_managed_mode(mock_is_managed_mode):
    mock_is_managed_mode.return_value = True

    with pytest.raises(RuntimeError):
        utils.confirm_with_user("prompt")


def test_get_host_tool(mock_which):
    mock_which.return_value = "/usr/bin/mybin"
    assert utils.get_host_tool("mybin") == "/usr/bin/mybin"


def test_get_host_tool_not_found(mock_which):
    mock_which.return_value = None
    with pytest.raises(errors.RockcraftError) as exc:
        utils.get_host_tool("mybin")
    assert str(exc.value) == "A tool Rockcraft depends on could not be found: 'mybin'"


@pytest.mark.parametrize(
    "target_dir",
    [
        "usr/local/bin",
        "usr/sbin",
        "usr/bin",
        "sbin",
        "bin",
    ],
)
def test_get_snap_tool(monkeypatch, tmp_path, target_dir):
    monkeypatch.setenv("SNAP_NAME", "rockcraft")
    monkeypatch.setenv("SNAP", str(tmp_path))

    dir_in_tmp_path = tmp_path / target_dir
    dir_in_tmp_path.mkdir(parents=True)

    bin_name = "mybin"

    expected_mybin = dir_in_tmp_path / bin_name
    expected_mybin.touch()

    mybin = utils.get_snap_tool(bin_name)

    assert mybin == str(expected_mybin)


def test_get_snap_tool_not_found(monkeypatch, tmp_path):
    monkeypatch.setenv("SNAP_NAME", "rockcraft")
    monkeypatch.setenv("SNAP", str(tmp_path))

    with pytest.raises(errors.RockcraftError) as exc:
        utils.get_snap_tool("non_existing")

    assert str(exc.value) == "Cannot find snap tool 'non_existing'"
