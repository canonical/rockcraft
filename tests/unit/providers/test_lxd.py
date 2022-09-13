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
import re
from unittest import mock
from unittest.mock import call

import pytest
from craft_providers import bases
from craft_providers.lxd import LXDError, LXDInstallationError

from rockcraft import providers
from rockcraft.providers import ProviderError

# pylint: disable=duplicate-code


@pytest.fixture()
def mock_buildd_base_configuration(mocker):
    with mock.patch(
        "rockcraft.providers._lxd.bases.BuilddBase", autospec=True
    ) as mock_base_config:
        mock_base_config.compatibility_tag = "buildd-base-v0"
        yield mock_base_config


@pytest.fixture()
def mock_configure_buildd_image_remote():
    with mock.patch(
        "craft_providers.lxd.configure_buildd_image_remote",
        return_value="buildd-remote",
    ) as mock_remote:
        yield mock_remote


@pytest.fixture
def mock_confirm_with_user():
    with mock.patch(
        "rockcraft.providers._lxd.confirm_with_user",
        return_value=False,
    ) as mock_confirm:
        yield mock_confirm


@pytest.fixture
def mock_lxc(monkeypatch):
    with mock.patch("craft_providers.lxd.LXC", autospec=True) as mock_lxc:
        yield mock_lxc.return_value


@pytest.fixture(autouse=True)
def mock_lxd_ensure_lxd_is_ready():
    with mock.patch(
        "craft_providers.lxd.ensure_lxd_is_ready", return_value=None
    ) as mock_is_ready:
        yield mock_is_ready


@pytest.fixture()
def mock_lxd_install():
    with mock.patch("craft_providers.lxd.install") as mock_install:
        yield mock_install


@pytest.fixture(autouse=True)
def mock_lxd_is_installed():
    with mock.patch(
        "craft_providers.lxd.is_installed", return_value=True
    ) as mock_is_installed:
        yield mock_is_installed


@pytest.fixture
def mock_lxd_launch():
    with mock.patch("craft_providers.lxd.launch", autospec=True) as mock_lxd_launch:
        yield mock_lxd_launch


def test_clean_project_environments_without_lxd(
    mock_lxc, mock_lxd_is_installed, mock_path
):
    mock_lxd_is_installed.return_value = False
    provider = providers.LXDProvider(
        lxc=mock_lxc, lxd_project="test-project", lxd_remote="test-remote"
    )

    assert (
        provider.clean_project_environments(
            project_name="my-rock",
            project_path=mock_path,
        )
        == []
    )

    assert mock_lxd_is_installed.mock_calls == [mock.call()]
    assert mock_lxc.mock_calls == []


def test_clean_project_environments(mock_lxc, mock_path):
    mock_lxc.list_names.return_value = [
        "do-not-delete-me-please",
        "rockcraft-testrock-445566",
        "rockcraft-my-rock-",
        "rockcraft-my-rock-445566",
        "rockcraft-my-rock-project-445566",
        "rockcraft_445566_a",
    ]
    provider = providers.LXDProvider(
        lxc=mock_lxc, lxd_project="test-project", lxd_remote="test-remote"
    )

    assert provider.clean_project_environments(
        project_name="my-rock-project",
        project_path=mock_path,
    ) == ["rockcraft-my-rock-project-445566"]

    assert mock_lxc.mock_calls == [
        mock.call.list_names(project="test-project", remote="test-remote"),
        mock.call.delete(
            instance_name="rockcraft-my-rock-project-445566",
            force=True,
            project="test-project",
            remote="test-remote",
        ),
    ]

    mock_lxc.reset_mock()

    assert provider.clean_project_environments(
        project_name="testrock",
        project_path=mock_path,
    ) == ["rockcraft-testrock-445566"]

    assert mock_lxc.mock_calls == [
        mock.call.list_names(project="test-project", remote="test-remote"),
        mock.call.delete(
            instance_name="rockcraft-testrock-445566",
            force=True,
            project="test-project",
            remote="test-remote",
        ),
    ]

    mock_lxc.reset_mock()

    assert (
        provider.clean_project_environments(
            project_name="unknown-rock",
            project_path=mock_path,
        )
        == []
    )
    assert mock_lxc.mock_calls == [
        mock.call.list_names(project="test-project", remote="test-remote"),
    ]


def test_clean_project_environments_list_failure(mock_lxc, mock_path):
    mock_lxc.list_names.side_effect = LXDError(brief="fail")
    provider = providers.LXDProvider(lxc=mock_lxc)

    with pytest.raises(ProviderError, match="fail"):
        provider.clean_project_environments(
            project_name="rock",
            project_path=mock_path,
        )


def test_clean_project_environments_delete_failure(mock_lxc, mock_path):
    error = LXDError("fail")
    mock_lxc.list_names.return_value = ["rockcraft-testrock-445566"]
    mock_lxc.delete.side_effect = error
    provider = providers.LXDProvider(lxc=mock_lxc)

    with pytest.raises(ProviderError, match="fail") as raised:
        provider.clean_project_environments(
            project_name="testrock",
            project_path=mock_path,
        )

    assert raised.value.__cause__ is error


def test_ensure_provider_is_available_ok_when_installed(mock_lxd_is_installed):
    mock_lxd_is_installed.return_value = True
    provider = providers.LXDProvider()

    provider.ensure_provider_is_available()


def test_ensure_provider_is_available_errors_when_user_declines(
    mock_confirm_with_user, mock_lxd_is_installed
):
    mock_confirm_with_user.return_value = False
    mock_lxd_is_installed.return_value = False
    provider = providers.LXDProvider()

    with pytest.raises(
        ProviderError,
        match=re.escape(
            "LXD is required, but not installed. Visit https://snapcraft.io/lxd for "
            "instructions on how to install the LXD snap for your distribution"
        ),
    ):
        provider.ensure_provider_is_available()

    assert mock_confirm_with_user.mock_calls == [
        mock.call(
            "LXD is required, but not installed. "
            "Do you wish to install LXD and configure it with the defaults?",
            default=False,
        )
    ]


def test_ensure_provider_is_available_errors_when_lxd_install_fails(
    mock_confirm_with_user, mock_lxd_is_installed, mock_lxd_install
):
    error = LXDInstallationError("foo")
    mock_confirm_with_user.return_value = True
    mock_lxd_is_installed.return_value = False
    mock_lxd_install.side_effect = error
    provider = providers.LXDProvider()

    with pytest.raises(
        ProviderError,
        match=re.escape(
            "Failed to install LXD. Visit https://snapcraft.io/lxd for "
            "instructions on how to install the LXD snap for your distribution"
        ),
    ) as raised:
        provider.ensure_provider_is_available()

    assert mock_confirm_with_user.mock_calls == [
        mock.call(
            "LXD is required, but not installed. "
            "Do you wish to install LXD and configure it with the defaults?",
            default=False,
        )
    ]
    assert raised.value.__cause__ is error


def test_ensure_provider_is_available_errors_when_lxd_not_ready(
    mock_confirm_with_user,
    mock_lxd_is_installed,
    mock_lxd_install,
    mock_lxd_ensure_lxd_is_ready,
):
    error = LXDError(
        brief="some error", details="some details", resolution="some resolution"
    )
    mock_confirm_with_user.return_value = True
    mock_lxd_is_installed.return_value = True
    mock_lxd_ensure_lxd_is_ready.side_effect = error
    provider = providers.LXDProvider()

    with pytest.raises(
        ProviderError,
        match=re.escape("some error\nsome details\nsome resolution"),
    ) as raised:
        provider.ensure_provider_is_available()

    assert raised.value.__cause__ is error


def test_get_command_environment_minimal(monkeypatch):
    monkeypatch.setenv("IGNORE_ME", "or-im-failing")
    monkeypatch.setenv("PATH", "not-using-host-path")
    provider = providers.LXDProvider()

    env = provider.get_command_environment()

    assert env == {
        "ROCKCRAFT_MANAGED_MODE": "1",
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
    }


def test_get_instance_name(mock_path):
    provider = providers.LXDProvider()

    assert (
        provider.get_instance_name(
            project_name="my-project-name",
            project_path=mock_path,
        )
        == "rockcraft-my-project-name-445566"
    )


@pytest.mark.parametrize("is_installed", [True, False])
def test_is_provider_available(is_installed, mock_lxd_is_installed):
    mock_lxd_is_installed.return_value = is_installed
    provider = providers.LXDProvider()

    assert provider.is_provider_available() == is_installed


@pytest.mark.parametrize(
    "channel,alias",
    [
        ("18.04", bases.BuilddBaseAlias.BIONIC),
        ("20.04", bases.BuilddBaseAlias.FOCAL),
        ("22.04", bases.BuilddBaseAlias.JAMMY),
    ],
)
def test_launched_environment(
    channel,
    alias,
    mock_buildd_base_configuration,
    mock_configure_buildd_image_remote,
    mock_lxd_launch,
    monkeypatch,
    tmp_path,
    mock_path,
    mocker,
):
    expected_environment = {
        "ROCKCRAFT_MANAGED_MODE": "1",
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
    }

    mocker.patch("sys.platform", "linux")
    mocker.patch(
        "rockcraft.providers._lxd.get_managed_environment_snap_channel",
        return_value="edge",
    )

    provider = providers.LXDProvider()

    with provider.launched_environment(
        project_name="test-rock",
        project_path=mock_path,
        build_base=f"ubuntu:{channel}",
    ) as instance:
        assert instance is not None
        assert mock_configure_buildd_image_remote.mock_calls == [mock.call()]
        assert mock_lxd_launch.mock_calls == [
            mock.call(
                name="rockcraft-test-rock-445566",
                base_configuration=mock_buildd_base_configuration.return_value,
                image_name=channel,
                image_remote="buildd-remote",
                auto_clean=True,
                auto_create_project=True,
                map_user_uid=True,
                uid=1234,
                use_snapshots=True,
                project="rockcraft",
                remote="local",
            ),
            mock.call().mount(
                host_source=mock_path, target=pathlib.Path("/root/project")
            ),
        ]
        assert mock_buildd_base_configuration.mock_calls == [
            call(
                alias=alias,
                compatibility_tag="rockcraft-buildd-base-v0.0",
                environment=expected_environment,
                hostname="rockcraft-test-rock-445566",
                snaps=[
                    bases.buildd.Snap(name="rockcraft", channel="edge", classic=True)
                ],
            )
        ]

        mock_lxd_launch.reset_mock()

    assert mock_lxd_launch.mock_calls == [
        mock.call().unmount_all(),
        mock.call().stop(),
    ]


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
def test_launched_environment_snap_channel(
    mock_buildd_base_configuration,
    mock_configure_buildd_image_remote,
    mock_lxd_launch,
    tmp_path,
    mocker,
    platform,
    snap_channel,
    expected_snap_channel,
):
    """Verify the rockcraft snap is installed from the correct channel."""
    mocker.patch("sys.platform", platform)
    mocker.patch(
        "rockcraft.providers._lxd.get_managed_environment_snap_channel",
        return_value=snap_channel,
    )

    provider = providers.LXDProvider()

    with provider.launched_environment(
        project_name="test-rock",
        project_path=tmp_path,
        build_base="ubuntu:20.04",
    ):
        assert mock_buildd_base_configuration.mock_calls == [
            call(
                alias=mock.ANY,
                compatibility_tag=mock.ANY,
                environment=mock.ANY,
                hostname=mock.ANY,
                snaps=[
                    bases.buildd.Snap(
                        name="rockcraft", channel=expected_snap_channel, classic=True
                    )
                ],
            )
        ]


def test_launched_environment_launch_base_configuration_error(
    mock_buildd_base_configuration,
    mock_configure_buildd_image_remote,
    mock_lxd_launch,
    tmp_path,
):
    error = bases.BaseConfigurationError(brief="fail")
    mock_lxd_launch.side_effect = error
    provider = providers.LXDProvider()

    with pytest.raises(ProviderError, match="fail") as raised:
        with provider.launched_environment(
            project_name="test-rock",
            project_path=tmp_path,
            build_base="ubuntu:20.04",
        ):
            pass

    assert raised.value.__cause__ is error


def test_launched_environment_launch_lxd_error(
    mock_buildd_base_configuration,
    mock_configure_buildd_image_remote,
    mock_lxd_launch,
    tmp_path,
):
    error = LXDError(brief="fail")
    mock_lxd_launch.side_effect = error
    provider = providers.LXDProvider()

    with pytest.raises(ProviderError, match="fail") as raised:
        with provider.launched_environment(
            project_name="test-rock",
            project_path=tmp_path,
            build_base="ubuntu:20.04",
        ):
            pass

    assert raised.value.__cause__ is error


def test_launched_environment_unmounts_and_stops_after_error(
    mock_buildd_base_configuration,
    mock_configure_buildd_image_remote,
    mock_lxd_launch,
    tmp_path,
):
    provider = providers.LXDProvider()

    with pytest.raises(RuntimeError):
        with provider.launched_environment(
            project_name="test-rock",
            project_path=tmp_path,
            build_base="ubuntu:20.04",
        ):
            mock_lxd_launch.reset_mock()
            raise RuntimeError("this is a test")

    assert mock_lxd_launch.mock_calls == [
        mock.call().unmount_all(),
        mock.call().stop(),
    ]


def test_launched_environment_unmount_all_error(
    mock_buildd_base_configuration,
    mock_configure_buildd_image_remote,
    mock_lxd_launch,
    tmp_path,
):
    error = LXDError(brief="fail")
    mock_lxd_launch.return_value.unmount_all.side_effect = error
    provider = providers.LXDProvider()

    with pytest.raises(ProviderError, match="fail") as raised:
        with provider.launched_environment(
            project_name="test-rock", project_path=tmp_path, build_base="ubuntu:20.04"
        ):
            pass

    assert raised.value.__cause__ is error


def test_launched_environment_stop_error(
    mock_buildd_base_configuration,
    mock_configure_buildd_image_remote,
    mock_lxd_launch,
    tmp_path,
):
    error = LXDError(brief="fail")
    mock_lxd_launch.return_value.stop.side_effect = error
    provider = providers.LXDProvider()

    with pytest.raises(ProviderError, match="fail") as raised:
        with provider.launched_environment(
            project_name="test-rock",
            project_path=tmp_path,
            build_base="ubuntu:22.04",
        ):
            pass

    assert raised.value.__cause__ is error
