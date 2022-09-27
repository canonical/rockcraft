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
from craft_providers import Executor, base

from rockcraft.providers import Provider


@pytest.fixture
def mock_instance():
    """Provide a mock instance (Executor)."""
    _mock_instance = mock.Mock(spec=Executor)
    yield _mock_instance


@pytest.fixture(autouse=True)
def fake_provider(mock_instance):
    """Fixture to provide a minimal fake provider."""

    class FakeProvider(Provider):
        """Fake provider."""

        def clean_project_environments(self, *, project_name: str, project_path: Path):
            pass

        @classmethod
        def ensure_provider_is_available(cls) -> None:
            pass

        @classmethod
        def is_provider_installed(cls) -> bool:
            return True

        @contextlib.contextmanager
        def launched_environment(
            self,
            *,
            project_name: str,
            project_path: Path,
            base_configuration: base.Base,
            build_base: str,
            instance_name: str,
        ):
            yield mock_instance

    return FakeProvider()
