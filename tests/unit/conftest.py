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

import contextlib
from pathlib import Path
from unittest import mock

import pytest
from craft_providers import Executor, Provider, base

# pylint: disable=import-outside-toplevel


@pytest.fixture
def mock_instance():
    """Provide a mock instance (Executor)."""
    return mock.Mock(spec=Executor)


@pytest.fixture
def mock_extensions(monkeypatch):
    from rockcraft.extensions import registry

    extensions_dict = {}
    monkeypatch.setattr(registry, "_EXTENSIONS", extensions_dict)

    return extensions_dict


@pytest.fixture(autouse=True)
def fake_provider(mock_instance):
    """Fixture to provide a minimal fake provider."""

    class FakeProvider(Provider):
        """Fake provider."""

        @property
        def name(self) -> str:
            return "fake"

        @property
        def install_recommendation(self) -> str:
            return "uninstallable"

        def clean_project_environments(self, *, instance_name: str):
            pass

        @classmethod
        def ensure_provider_is_available(cls) -> None:
            pass

        @classmethod
        def is_provider_installed(cls) -> bool:
            return True

        def create_environment(self, *, instance_name: str):  # type: ignore[reportIncompatibleVariableOverride]
            yield mock_instance

        @contextlib.contextmanager  # type: ignore[misc]
        def launched_environment(
            self,
            *,
            project_name: str,
            project_path: Path,
            base_configuration: base.Base,
            instance_name: str,
            allow_unstable: bool = False,
            shutdown_delay_mins: int | None = None,
        ):
            yield mock_instance

    return FakeProvider()
