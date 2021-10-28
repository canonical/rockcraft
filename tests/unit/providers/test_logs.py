# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021 Canonical Ltd.
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
from unittest import mock

import pytest
from craft_cli import messages

import rockcraft.ui
from rockcraft import providers


@pytest.fixture
def mock_namedtemporaryfile(mocker, new_dir):
    mock_namedtemp = mocker.patch(
        "rockcraft.providers._logs.tempfile.NamedTemporaryFile"
    )
    mock_namedtemp.return_value.__enter__.return_value.name = str(new_dir / "fake.file")
    yield mock_namedtemp


def test_capture_logs_from_instance(
    mocker, emitter, mock_instance, mock_namedtemporaryfile, new_dir
):
    fake_log = new_dir / "fake.file"
    fake_log_data = "some\nlog data\nhere"
    fake_log.write_text(fake_log_data, encoding="utf-8")

    mocker.patch.object(rockcraft.ui, "emit", messages.emit)
    providers.capture_logs_from_instance(mock_instance)

    assert mock_instance.mock_calls == [
        mock.call.pull_file(
            source=pathlib.Path("/tmp/rockcraft.log"), destination=fake_log
        ),
    ]
    expected = [
        "Logs captured from managed instance:",
        ":: some",
        ":: log data",
        ":: here",
    ]
    emitter.assert_recorded(expected)
    assert mock_namedtemporaryfile.mock_calls == [
        mock.call(delete=False, prefix="rockcraft-"),
        mock.call().__enter__(),
        mock.call().__exit__(None, None, None),
    ]


def test_capture_logs_from_instance_not_found(
    mocker, emitter, mock_instance, mock_namedtemporaryfile, new_dir
):
    fake_log = new_dir / "fake.file"
    mock_instance.pull_file.side_effect = FileNotFoundError()

    mocker.patch.object(rockcraft.ui, "emit", messages.emit)
    providers.capture_logs_from_instance(mock_instance)

    assert mock_instance.mock_calls == [
        mock.call.pull_file(
            source=pathlib.Path("/tmp/rockcraft.log"), destination=fake_log
        ),
    ]
    emitter.assert_recorded(["No logs found in instance."])
