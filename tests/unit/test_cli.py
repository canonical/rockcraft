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
from argparse import Namespace
from unittest.mock import call

import pytest
from craft_cli import emit

from rockcraft import cli


@pytest.mark.parametrize("cmd", ["pull", "overlay", "build", "stage", "prime"])
def test_run_command(mocker, cmd):
    run_mock = mocker.patch("rockcraft.lifecycle.run")
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", cmd])
    cli.run()

    assert run_mock.mock_calls == [
        call(cmd, Namespace(parts=[], shell=False, shell_after=False))
    ]
    assert mock_ended_ok.mock_calls == [call()]


@pytest.mark.parametrize("cmd", ["pull", "overlay", "build", "stage", "prime"])
def test_run_command_parts(mocker, cmd):
    run_mock = mocker.patch("rockcraft.lifecycle.run")
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", cmd, "part1", "part2"])
    cli.run()

    assert run_mock.mock_calls == [
        call(cmd, Namespace(parts=["part1", "part2"], shell=False, shell_after=False))
    ]
    assert mock_ended_ok.mock_calls == [call()]


@pytest.mark.parametrize("cmd", ["pull", "overlay", "build", "stage", "prime"])
def test_run_command_shell(mocker, cmd):
    run_mock = mocker.patch("rockcraft.lifecycle.run")
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", cmd, "--shell"])
    cli.run()

    assert run_mock.mock_calls == [
        call(cmd, Namespace(parts=[], shell=True, shell_after=False))
    ]
    assert mock_ended_ok.mock_calls == [call()]


@pytest.mark.parametrize("cmd", ["pull", "overlay", "build", "stage", "prime"])
def test_run_command_shell_after(mocker, cmd):
    run_mock = mocker.patch("rockcraft.lifecycle.run")
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", cmd, "--shell-after"])
    cli.run()

    assert run_mock.mock_calls == [
        call(cmd, Namespace(parts=[], shell=False, shell_after=True))
    ]
    assert mock_ended_ok.mock_calls == [call()]


def test_run_pack(mocker):
    run_mock = mocker.patch("rockcraft.lifecycle.run")
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", "pack"])
    cli.run()

    assert run_mock.mock_calls == [call("pack", Namespace())]
    assert mock_ended_ok.mock_calls == [call()]
