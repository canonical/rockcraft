# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2021-2022 Canonical Ltd
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

import os
from pathlib import Path

import pytest
import xdg  # type: ignore


@pytest.fixture()
def new_dir(tmpdir):
    """Change to a new temporary directory."""

    cwd = os.getcwd()
    os.chdir(tmpdir)

    yield tmpdir

    os.chdir(cwd)


@pytest.fixture(autouse=True)
def temp_xdg(tmpdir, mocker):
    """Use a temporary location for XDG directories."""

    mocker.patch(
        "xdg.BaseDirectory.xdg_config_home", new=os.path.join(tmpdir, ".config")
    )
    mocker.patch("xdg.BaseDirectory.xdg_data_home", new=os.path.join(tmpdir, ".local"))
    mocker.patch("xdg.BaseDirectory.xdg_cache_home", new=os.path.join(tmpdir, ".cache"))
    mocker.patch(
        "xdg.BaseDirectory.xdg_config_dirs",
        new=[xdg.BaseDirectory.xdg_config_home],  # pyright: ignore
    )
    mocker.patch(
        "xdg.BaseDirectory.xdg_data_dirs",
        new=[xdg.BaseDirectory.xdg_data_home],  # pyright: ignore
    )
    mocker.patch.dict(os.environ, {"XDG_CONFIG_HOME": os.path.join(tmpdir, ".config")})


@pytest.fixture()
def reset_callbacks():
    """Fixture that resets the status of craft-part's various lifecycle callbacks,
    so that tests can start with a clean slate.
    """
    # pylint: disable=import-outside-toplevel

    from craft_parts import callbacks

    callbacks.unregister_all()
    yield
    callbacks.unregister_all()


class RecordingEmitter:
    """Record what is shown using the emitter and provide a nice API for tests."""

    def __init__(self):
        self.progress = []
        self.message = []
        self.trace = []
        self.emitted = []
        self.raw = []

    def record(self, level, text):
        """Record the text for the specific level and in the general storages."""
        getattr(self, level).append(text)
        self.emitted.append(text)
        self.raw.append((level, text))

    def _check(self, expected, storage):
        """Really verify messages."""
        for pos, recorded_msg in enumerate(storage):
            if recorded_msg == expected[0]:
                break
        else:
            raise AssertionError(f"Initial test message not found in {storage}")

        recorded = storage[pos : pos + len(expected)]  # pylint: disable=W0631
        assert recorded == expected

    def assert_recorded(self, expected):
        """Verify that the given messages were recorded consecutively."""
        self._check(expected, self.emitted)

    def assert_recorded_raw(self, expected):
        """Verify that the given messages (with specific level) were recorded consecutively."""
        self._check(expected, self.raw)


@pytest.fixture()
def extra_project_params():
    """Configuration fixture for the Project used by the default services."""
    return {}


@pytest.fixture()
def default_project(extra_project_params):
    from craft_application.models import VersionStr
    from rockcraft.models.project import NameStr, Project

    parts = extra_project_params.pop("parts", {})

    return Project(
        name=NameStr("default"),
        version=VersionStr("1.0"),
        summary="default project",
        description="default project",
        base="ubuntu@22.04",
        parts=parts,
        license="MIT",
        platforms={"amd64": None},
        **extra_project_params,
    )


@pytest.fixture()
def default_build_plan(default_project):
    from rockcraft.models.project import BuildPlanner

    return BuildPlanner.unmarshal(default_project.marshal()).get_build_plan()


@pytest.fixture()
def default_factory(default_project, default_build_plan):
    from rockcraft.application import APP_METADATA
    from rockcraft.services import RockcraftServiceFactory

    factory = RockcraftServiceFactory(
        app=APP_METADATA,
        project=default_project,
    )
    factory.set_kwargs("image", work_dir=Path("work"), build_plan=default_build_plan)
    return factory


@pytest.fixture()
def default_image_info():
    from rockcraft import oci
    from rockcraft.services.image import ImageInfo

    return ImageInfo(
        base_image=oci.Image(image_name="fake_image", path=Path()),
        base_layer_dir=Path(),
        base_digest=b"deadbeef",
    )


@pytest.fixture()
def default_application(default_factory, default_project):
    from rockcraft.application import APP_METADATA, Rockcraft

    return Rockcraft(APP_METADATA, default_factory)


@pytest.fixture()
def image_service(default_project, default_factory, tmp_path, default_build_plan):
    from rockcraft.application import APP_METADATA
    from rockcraft.services import RockcraftImageService

    return RockcraftImageService(
        app=APP_METADATA,
        project=default_project,
        services=default_factory,
        work_dir=tmp_path,
        build_plan=default_build_plan,
    )


@pytest.fixture()
def provider_service(default_project, default_build_plan, default_factory, tmp_path):
    from rockcraft.application import APP_METADATA
    from rockcraft.services import RockcraftProviderService

    return RockcraftProviderService(
        app=APP_METADATA,
        project=default_project,
        services=default_factory,
        build_plan=default_build_plan,
        work_dir=tmp_path,
    )


@pytest.fixture()
def package_service(default_project, default_factory, default_build_plan):
    from rockcraft.application import APP_METADATA
    from rockcraft.services import RockcraftPackageService

    return RockcraftPackageService(
        app=APP_METADATA,
        project=default_project,
        services=default_factory,
        build_plan=default_build_plan,
    )


@pytest.fixture()
def lifecycle_service(default_project, default_factory, default_build_plan):
    from rockcraft.application import APP_METADATA
    from rockcraft.services import RockcraftLifecycleService

    return RockcraftLifecycleService(
        app=APP_METADATA,
        project=default_project,
        services=default_factory,
        work_dir=Path("work/"),
        cache_dir=Path("cache/"),
        build_plan=default_build_plan,
    )


@pytest.fixture()
def mock_obtain_image(default_factory, mocker):
    """Mock and return the "obtain_image()" method of the default image service."""
    image_service = default_factory.image
    return mocker.patch.object(image_service, "obtain_image")


@pytest.fixture()
def run_lifecycle(mocker, default_build_plan):
    """Helper to call testing.run_mocked_lifecycle()."""

    def _inner(**kwargs):
        from craft_application.util import get_host_base

        from tests.testing.lifecycle import run_mocked_lifecycle

        for build_plan in default_build_plan:
            build_plan.base = get_host_base()

        return run_mocked_lifecycle(
            mocker=mocker, build_plan=default_build_plan, **kwargs
        )

    return _inner


@pytest.fixture(autouse=True)
def reset_features():
    from craft_parts import Features

    Features.reset()
    yield
    Features.reset()


@pytest.fixture()
def enable_overlay_feature(reset_features):
    """Enable the overlay feature."""
    from craft_parts import Features

    Features(enable_overlay=True)
