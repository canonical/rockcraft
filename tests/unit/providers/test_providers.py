# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2022 Canonical Ltd.
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
from unittest.mock import MagicMock, Mock, call

import pytest
from craft_providers import bases

from rockcraft.providers import providers


def test_get_command_environment_minimal(monkeypatch):
    monkeypatch.setenv("IGNORE_ME", "or-im-failing")
    monkeypatch.setenv("PATH", "not-using-host-path")

    assert providers.get_command_environment() == {
        "ROCKCRAFT_MANAGED_MODE": "1",
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
    }


def test_get_command_environment_all_opts(monkeypatch):
    monkeypatch.setenv("IGNORE_ME", "or-im-failing")
    monkeypatch.setenv("PATH", "not-using-host-path")
    monkeypatch.setenv("http_proxy", "test-http-proxy")
    monkeypatch.setenv("https_proxy", "test-https-proxy")
    monkeypatch.setenv("no_proxy", "test-no-proxy")

    assert providers.get_command_environment() == {
        "ROCKCRAFT_MANAGED_MODE": "1",
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
        "http_proxy": "test-http-proxy",
        "https_proxy": "test-https-proxy",
        "no_proxy": "test-no-proxy",
    }


def test_get_instance_name(mock_path):
    assert (
        providers.get_instance_name(
            project_name="my-project-name",
            project_path=mock_path,
        )
        == "rockcraft-my-project-name-445566"
    )


def test_capture_logs_from_instance(mocker, emitter, mock_instance, new_dir):
    """Verify logs from an instance are retrieved and emitted."""
    fake_log = Path(new_dir / "fake.file")
    fake_log_data = "some\nlog data\nhere"
    fake_log.write_text(fake_log_data, encoding="utf-8")

    mock_instance.temporarily_pull_file = MagicMock()
    mock_instance.temporarily_pull_file.return_value = fake_log

    providers.capture_logs_from_instance(mock_instance)

    assert mock_instance.mock_calls == [
        call.temporarily_pull_file(source=Path("/tmp/rockcraft.log"), missing_ok=True)
    ]
    expected = [
        call("trace", "Logs retrieved from managed instance:"),
        call("trace", ":: some"),
        call("trace", ":: log data"),
        call("trace", ":: here"),
    ]
    emitter.assert_interactions(expected)


def test_capture_log_from_instance_not_found(mocker, emitter, mock_instance, new_dir):
    """Verify a missing log file is handled properly."""
    mock_instance.temporarily_pull_file = MagicMock(return_value=None)
    mock_instance.temporarily_pull_file.return_value = (
        mock_instance.temporarily_pull_file
    )
    mock_instance.temporarily_pull_file.__enter__ = Mock(return_value=None)

    providers.capture_logs_from_instance(mock_instance)

    emitter.assert_trace("Could not find log file /tmp/rockcraft.log in instance.")
    mock_instance.temporarily_pull_file.assert_called_with(
        source=Path("/tmp/rockcraft.log"), missing_ok=True
    )


@pytest.mark.parametrize(
    "platform, snap_channel, expected_snap_channel",
    [
        ("linux", None, None),
        ("linux", "edge", "edge"),
        ("darwin", "edge", "edge"),
        # default to stable on non-linux system
        ("darwin", None, "stable"),
    ],
)
@pytest.mark.parametrize(
    "alias",
    [
        bases.BuilddBaseAlias.BIONIC,
        bases.BuilddBaseAlias.FOCAL,
        bases.BuilddBaseAlias.JAMMY,
    ],
)
def test_get_base_configuration(
    platform,
    snap_channel,
    expected_snap_channel,
    alias,
    tmp_path,
    mocker,
):
    """Verify the rockcraft snap is installed from the correct channel."""
    mocker.patch("sys.platform", platform)
    mocker.patch(
        "rockcraft.providers.providers.get_managed_environment_snap_channel",
        return_value=snap_channel,
    )
    mocker.patch(
        "rockcraft.providers.providers.get_command_environment",
        return_value="test-env",
    )
    mocker.patch(
        "rockcraft.providers.providers.get_instance_name",
        return_value="test-instance-name",
    )
    mock_buildd_base = mocker.patch("rockcraft.providers.providers.bases.BuilddBase")
    mock_buildd_base.compatibility_tag = "buildd-base-v0"

    providers.get_base_configuration(
        alias=alias, project_name="test-name", project_path=tmp_path
    )

    mock_buildd_base.assert_called_with(
        alias=alias,
        compatibility_tag="rockcraft-buildd-base-v0.0",
        environment="test-env",
        hostname="test-instance-name",
        snaps=[
            bases.buildd.Snap(
                name="rockcraft", channel=expected_snap_channel, classic=True
            )
        ],
    )
