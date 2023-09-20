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
from typing import Optional
from unittest import mock

import pytest
from craft_providers import Executor, Provider, base

# pylint: disable=import-outside-toplevel


@pytest.fixture
def mock_instance():
    """Provide a mock instance (Executor)."""
    _mock_instance = mock.Mock(spec=Executor)
    yield _mock_instance


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

        def create_environment(self, *, instance_name: str):
            yield mock_instance

        @contextlib.contextmanager  # type: ignore[misc]
        def launched_environment(
            self,
            *,
            project_name: str,
            project_path: Path,
            base_configuration: base.Base,
            build_base: Optional[str] = None,
            instance_name: str,
            allow_unstable: bool = False,
        ):
            yield mock_instance

    return FakeProvider()


@pytest.fixture
def default_project():
    from rockcraft import models

    return models.Project(  # type: ignore[reportGeneralTypeIssues]
        name="default",
        version="1.0",
        summary="default project",
        description="default project",
        base="ubuntu:22.04",
        parts={},
        license="MIT",
        platforms={"amd64": None},
    )


@pytest.fixture
def default_factory(default_project):
    from rockcraft.application import APP_METADATA
    from rockcraft.services import RockcraftServiceFactory

    return RockcraftServiceFactory(
        app=APP_METADATA,
        project=default_project,
    )


@pytest.fixture
def image_service(default_project, default_factory, tmp_path):
    from rockcraft.application import APP_METADATA
    from rockcraft.services import RockcraftImageService

    return RockcraftImageService(
        app=APP_METADATA,
        project=default_project,
        services=default_factory,
        work_dir=tmp_path,
        build_for="amd64",
    )
