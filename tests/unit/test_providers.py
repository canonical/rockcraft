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
from craft_providers import ProviderError, bases
from craft_providers.lxd import LXDProvider
from craft_providers.multipass import MultipassProvider

from rockcraft import providers


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


def test_get_instance_name(tmp_path):
    assert (
        providers.get_instance_name(
            project_name="my-project-name",
            project_path=tmp_path,
        )
        == f"rockcraft-my-project-name-{tmp_path.stat().st_ino}"
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
        call("debug", "Logs retrieved from managed instance:"),
        call("debug", ":: some"),
        call("debug", ":: log data"),
        call("debug", ":: here"),
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

    emitter.assert_debug("Could not find log file /tmp/rockcraft.log in instance.")
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
        "rockcraft.providers.get_managed_environment_snap_channel",
        return_value=snap_channel,
    )
    mocker.patch(
        "rockcraft.providers.get_command_environment",
        return_value="test-env",
    )
    mocker.patch(
        "rockcraft.providers.get_instance_name",
        return_value="test-instance-name",
    )
    mock_buildd_base = mocker.patch("rockcraft.providers.bases.BuilddBase")
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


@pytest.mark.parametrize(
    "is_provider_installed, confirm_with_user",
    [(True, True), (True, False), (False, True)],
)
def test_ensure_provider_is_available_lxd(
    is_provider_installed, confirm_with_user, mocker
):
    """Verify LXD is ensured to be available when LXD is installed or the user chooses
    to install LXD."""
    mock_lxd_provider = Mock(spec=LXDProvider)
    mocker.patch(
        "rockcraft.providers.LXDProvider.is_provider_installed",
        return_value=is_provider_installed,
    )
    mocker.patch(
        "rockcraft.providers.confirm_with_user",
        return_value=confirm_with_user,
    )
    mock_ensure_provider_is_available = mocker.patch(
        "rockcraft.providers.ensure_provider_is_available"
    )

    providers.ensure_provider_is_available(mock_lxd_provider)

    mock_ensure_provider_is_available.assert_called_once()


def test_ensure_provider_is_available_lxd_error(mocker):
    """Raise an error if the user does not choose to install LXD."""
    mock_lxd_provider = Mock(spec=LXDProvider)
    mocker.patch(
        "rockcraft.providers.LXDProvider.is_provider_installed",
        return_value=False,
    )
    mocker.patch("rockcraft.providers.confirm_with_user", return_value=False)

    with pytest.raises(ProviderError) as error:
        providers.ensure_provider_is_available(mock_lxd_provider)

    assert error.value.brief == (
        "LXD is required, but not installed. Visit https://snapcraft.io/lxd for "
        "instructions on how to install the LXD snap for your distribution"
    )


@pytest.mark.parametrize(
    "is_provider_installed, confirm_with_user",
    [(True, True), (True, False), (False, True)],
)
def test_ensure_provider_is_available_multipass(
    is_provider_installed, confirm_with_user, mocker
):
    """Verify Multipass is ensured to be available when Multipass is installed or the
    user chooses to install Multipass."""
    mock_multipass_provider = Mock(spec=MultipassProvider)
    mocker.patch(
        "rockcraft.providers.MultipassProvider.is_provider_installed",
        return_value=is_provider_installed,
    )
    mocker.patch(
        "rockcraft.providers.confirm_with_user",
        return_value=confirm_with_user,
    )
    mock_ensure_provider_is_available = mocker.patch(
        "rockcraft.providers.ensure_provider_is_available"
    )

    providers.ensure_provider_is_available(mock_multipass_provider)

    mock_ensure_provider_is_available.assert_called_once()


def test_ensure_provider_is_available_multipass_error(mocker):
    """Raise an error if the user does not choose to install Multipass."""
    mock_multipass_provider = Mock(spec=MultipassProvider)
    mocker.patch(
        "rockcraft.providers.MultipassProvider.is_provider_installed",
        return_value=False,
    )
    mocker.patch("rockcraft.providers.confirm_with_user", return_value=False)

    with pytest.raises(ProviderError) as error:
        providers.ensure_provider_is_available(mock_multipass_provider)

    assert error.value.brief == (
        "Multipass is required, but not installed. Visit https://multipass.run/for "
        "instructions on installing Multipass for your operating system."
    )


def test_ensure_provider_is_available_unknown_error():
    """Raise an error if the provider type is unknown."""
    mock_multipass_provider = Mock()

    with pytest.raises(ProviderError) as error:
        providers.ensure_provider_is_available(mock_multipass_provider)

    assert error.value.brief == "cannot install unknown provider"


def test_get_provider_default_lxd(emitter, mocker):
    """Verify lxd is the default provider when running on a linux system."""
    mocker.patch("sys.platform", "linux")
    provider = providers.get_provider()
    assert isinstance(provider, LXDProvider)
    assert provider.lxd_project == "rockcraft"
    emitter.assert_debug("Using default provider 'lxd' on linux system")


@pytest.mark.parametrize("system", ["darwin", "win32", "other-system"])
def test_get_provider_default_multipass(emitter, mocker, system):
    """Verify multipass is the default provider when running on a non-linux system."""
    mocker.patch("sys.platform", system)
    assert isinstance(providers.get_provider(), MultipassProvider)
    emitter.assert_debug("Using default provider 'multipass' on non-linux system")


def test_get_provider_environmental_variable(monkeypatch):
    """Verify the provider can be set by an environmental variable."""
    monkeypatch.setenv("ROCKCRAFT_PROVIDER", "lxd")
    provider = providers.get_provider()
    assert isinstance(provider, LXDProvider)
    assert provider.lxd_project == "rockcraft"

    monkeypatch.setenv("ROCKCRAFT_PROVIDER", "multipass")
    assert isinstance(providers.get_provider(), MultipassProvider)


def test_get_provider_error(monkeypatch):
    """Raise a ValueError when an invalid provider is passed."""
    monkeypatch.setenv("ROCKCRAFT_PROVIDER", "invalid-provider")

    with pytest.raises(ValueError) as error:
        providers.get_provider()

    assert str(error.value) == "unsupported provider specified: 'invalid-provider'"
