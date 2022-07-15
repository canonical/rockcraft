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

import re
import sys
from unittest import mock
from unittest.mock import call

import pytest
from craft_providers import bases
from craft_providers.actions import snap_installer

from rockcraft import providers


@pytest.fixture
def mock_inject():
    with mock.patch(
        "craft_providers.actions.snap_installer.inject_from_host"
    ) as mock_inject:
        yield mock_inject


@pytest.fixture
def mock_install_from_store():
    with mock.patch(
        "craft_providers.actions.snap_installer.install_from_store"
    ) as mock_install:
        yield mock_install


@pytest.mark.parametrize(
    "alias",
    [
        bases.BuilddBaseAlias.BIONIC,
        bases.BuilddBaseAlias.FOCAL,
        bases.BuilddBaseAlias.JAMMY,
    ],
)
def test_base_configuration_setup_inject_from_host(
    mock_instance, mock_inject, mock_install_from_store, monkeypatch, alias
):
    monkeypatch.setattr(sys, "platform", "linux")

    config = providers.RockcraftBuilddBaseConfiguration(alias=alias)
    config.setup(executor=mock_instance)

    assert mock_inject.mock_calls == [
        call(executor=mock_instance, snap_name="rockcraft", classic=True)
    ]
    assert mock_install_from_store.mock_calls == []

    assert config.compatibility_tag == "rockcraft-buildd-base-v0.0"


@pytest.mark.parametrize(
    "alias",
    [
        bases.BuilddBaseAlias.BIONIC,
        bases.BuilddBaseAlias.FOCAL,
        bases.BuilddBaseAlias.JAMMY,
    ],
)
def test_base_configuration_setup_from_store(
    mock_instance, mock_inject, mock_install_from_store, monkeypatch, alias
):
    channel = "test-track/test-channel"
    monkeypatch.setenv("ROCKCRAFT_INSTALL_SNAP_CHANNEL", channel)

    config = providers.RockcraftBuilddBaseConfiguration(alias=alias)
    config.setup(executor=mock_instance)

    assert mock_inject.mock_calls == []
    assert mock_install_from_store.mock_calls == [
        call(
            executor=mock_instance, snap_name="rockcraft", channel=channel, classic=True
        )
    ]

    assert config.compatibility_tag == "rockcraft-buildd-base-v0.0"


@pytest.mark.parametrize(
    "alias",
    [
        bases.BuilddBaseAlias.BIONIC,
        bases.BuilddBaseAlias.FOCAL,
        bases.BuilddBaseAlias.JAMMY,
    ],
)
def test_base_configuration_setup_from_store_default_for_windows(
    mock_instance, mock_inject, mock_install_from_store, monkeypatch, alias
):
    monkeypatch.setattr(sys, "platform", "win32")

    config = providers.RockcraftBuilddBaseConfiguration(alias=alias)
    config.setup(executor=mock_instance)

    assert mock_inject.mock_calls == []
    assert mock_install_from_store.mock_calls == [
        call(
            executor=mock_instance,
            snap_name="rockcraft",
            channel="stable",
            classic=True,
        )
    ]

    assert config.compatibility_tag == "rockcraft-buildd-base-v0.0"


def test_base_configuration_setup_snap_injection_error(
    mock_instance, mock_inject, monkeypatch
):
    monkeypatch.setattr(sys, "platform", "linux")

    alias = bases.BuilddBaseAlias.FOCAL
    config = providers.RockcraftBuilddBaseConfiguration(alias=alias)
    mock_inject.side_effect = snap_installer.SnapInstallationError(brief="foo error")

    with pytest.raises(
        bases.BaseConfigurationError,
        match=r"Failed to inject host rockcraft snap into target environment.",
    ) as raised:
        config.setup(executor=mock_instance)

    assert raised.value.__cause__ is not None


def test_base_configuration_setup_snap_install_from_store_error(
    mock_instance, mock_install_from_store, monkeypatch
):
    channel = "test-track/test-channel"
    monkeypatch.setenv("ROCKCRAFT_INSTALL_SNAP_CHANNEL", channel)
    alias = bases.BuilddBaseAlias.FOCAL
    config = providers.RockcraftBuilddBaseConfiguration(alias=alias)
    mock_install_from_store.side_effect = snap_installer.SnapInstallationError(
        brief="foo error"
    )
    match = re.escape(
        "Failed to install rockcraft snap from store channel "
        "'test-track/test-channel' into target environment."
    )

    with pytest.raises(
        bases.BaseConfigurationError,
        match=match,
    ) as raised:
        config.setup(executor=mock_instance)

    assert raised.value.__cause__ is not None
