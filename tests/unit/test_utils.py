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

import re
from pathlib import Path

import pytest
from rockcraft import utils


@pytest.fixture
def mock_isatty(mocker):
    return mocker.patch("rockcraft.utils.sys.stdin.isatty", return_value=True)


@pytest.fixture
def mock_input(mocker):
    return mocker.patch("rockcraft.utils.input", return_value="")


@pytest.fixture
def mock_is_managed_mode(mocker):
    return mocker.patch("rockcraft.utils.is_managed_mode", return_value=False)


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


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("echo", (["echo"], None)),
        ("echo [ ]", (["echo"], [])),
        ("echo foo", (["echo", "foo"], None)),
        ("echo [ foo ]", (["echo"], ["foo"])),
        ("echo '[ foo ]' [ bar ]", (["echo", "[ foo ]"], ["bar"])),
        ("echo [ foo [bar] ]", (["echo"], ["foo", "[bar]"])),
        ("[ echo foo ]", ([], ["echo", "foo"])),
        ("echo happy :-] [ sad :-[ ]", (["echo", "happy", ":-]"], ["sad", ":-["])),
        ("[ ]", ([], [])),
        ("", ([], None)),
    ],
)
def test_parse_command(command, expected):
    assert utils.parse_command(command) == expected


@pytest.mark.parametrize(
    ("command", "exception", "expected"),
    [
        (
            "echo ] wrong syntax [",
            IndexError,
            "Bad syntax for the command's additional args.",
        ),
        ("echo [ foo [ bar ] ]", ValueError, "Cannot nest [ ... ] groups."),
        (
            "echo [ foo ] extra-foo",
            ValueError,
            "Cannot have any arguments after [ ... ] group.",
        ),
        ("echo 'Unclosed string", ValueError, "No closing quotation"),  # from shlex
    ],
)
def test_parse_command_invalid(command, exception, expected):
    with pytest.raises(exception, match=re.escape(expected)):
        utils.parse_command(command)
