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
import types
from pathlib import Path
from typing import Any
from unittest import mock

import craft_platforms
import distro
import pytest
import xdg
from craft_application.application import AppMetadata
from craft_application.services import ServiceFactory
from overrides import override
from rockcraft import services
from rockcraft.application import APP_METADATA, Rockcraft

DEFAULT_PROJECT_TEMPLATE = """\
name: test-rock
version: "0.1"
summary: Rock on!
description: Ramble off!
base: {base}
platforms:
  risky:
    build-on: [amd64, arm64, ppc64el, riscv64, s390x]
    build-for: [riscv64]
"""


@pytest.fixture
def new_dir(tmpdir):
    """Change to a new temporary directory."""

    cwd = Path.cwd()
    os.chdir(tmpdir)

    yield tmpdir

    os.chdir(cwd)


@pytest.fixture(autouse=True)
def temp_xdg(tmp_path, mocker):
    """Use a temporary location for XDG directories."""

    mocker.patch("xdg.BaseDirectory.xdg_config_home", new=str(tmp_path / ".config"))
    mocker.patch("xdg.BaseDirectory.xdg_data_home", new=str(tmp_path / ".local"))
    mocker.patch("xdg.BaseDirectory.xdg_cache_home", new=str(tmp_path / ".cache"))
    mocker.patch(
        "xdg.BaseDirectory.xdg_config_dirs",
        new=[xdg.BaseDirectory.xdg_config_home],
    )
    mocker.patch(
        "xdg.BaseDirectory.xdg_data_dirs",
        new=[xdg.BaseDirectory.xdg_data_home],
    )
    mocker.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmp_path / ".config")})


@pytest.fixture
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
        for pos, recorded_msg in enumerate(storage):  # noqa: B007
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


@pytest.fixture
def extra_project_params():
    """Configuration fixture for the Project used by the default services."""
    return {}


@pytest.fixture
def default_project(extra_project_params):
    from rockcraft.models.project import Project

    parts = extra_project_params.pop("parts", {})

    return Project.unmarshal(
        {
            "name": "default",
            "version": "1.0",
            "summary": "default project",
            "description": "default project",
            "base": "ubuntu@22.04",
            "parts": parts,
            "license": "MIT",
            "platforms": {"amd64": {"build-on": ["amd64"], "build-for": ["amd64"]}},
            **extra_project_params,
        }
    )


@pytest.fixture
def default_image_info():
    from rockcraft import oci
    from rockcraft.services.image import ImageInfo

    return ImageInfo(
        base_image=oci.Image(image_name="fake_image", path=Path()),
        base_layer_dir=Path(),
        base_digest=b"deadbeef",
    )


@pytest.fixture
def mock_obtain_image(fake_services, mocker):
    """Mock and return the "obtain_image()" method of the default image service."""
    image_service = fake_services.image
    return mocker.patch.object(image_service, "obtain_image")


@pytest.fixture
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


@pytest.fixture
def enable_overlay_feature(reset_features):
    """Enable the overlay feature."""
    from craft_parts import Features

    Features(enable_overlay=True)


@pytest.fixture
def project_main_module() -> types.ModuleType:
    """Fixture that returns the project's principal package (imported).

    This fixture should be rewritten by "downstream" projects to return the correct
    module. Then, every test that uses this fixture will correctly test against the
    downstream project.
    """
    try:
        # This should be the project's main package; downstream projects must update this.
        import rockcraft

        main_module = rockcraft
    except ImportError:
        pytest.fail(
            "Failed to import the project's main module: check if it needs updating",
        )
    return main_module


@pytest.fixture
def fake_provider_service_class(
    project_path: Path,
) -> type[services.RockcraftProviderService]:
    class FakeProviderService(services.RockcraftProviderService):
        def __init__(
            self,
            app: AppMetadata,
            services: ServiceFactory,
            work_dir: Path,
        ):
            super().__init__(app, services, work_dir=project_path)

    return FakeProviderService


@pytest.fixture
def fake_package_service_class() -> type[services.RockcraftPackageService]:
    class FakePackageService(services.RockcraftPackageService):
        pass

    return FakePackageService


@pytest.fixture
def fake_remote_build_service_class(
    mocker,
) -> type[services.RockcraftRemoteBuildService]:
    import lazr.restfulclient.resource

    me = mock.Mock(lazr.restfulclient.resource.Entry)
    me.name = "craft_test_user"

    class FakeRemoteBuildService(services.RockcraftRemoteBuildService):
        @override
        def __init__(self, app: AppMetadata, services: ServiceFactory):
            super().__init__(app=app, services=services)
            self._is_setup = True

    # The login should not do anything
    mocker.patch("craft_application.launchpad.Launchpad.anonymous")
    mocker.patch("craft_application.launchpad.Launchpad.login")

    return FakeRemoteBuildService


@pytest.fixture
def fake_services(
    in_project_path,
    fake_package_service_class,
    fake_provider_service_class,
    fake_remote_build_service_class,
    mocker,
    default_image_info,
) -> services.RockcraftServiceFactory:
    from rockcraft.services import RockcraftServiceFactory, register_rockcraft_services

    # Register the defaults
    register_rockcraft_services()

    # Override defaults with the classes that need modifications for testing
    RockcraftServiceFactory.register("package", fake_package_service_class)
    RockcraftServiceFactory.register("remote_build", fake_remote_build_service_class)
    RockcraftServiceFactory.register("provider", fake_provider_service_class)
    RockcraftServiceFactory.register("image", services.RockcraftImageService)

    factory = RockcraftServiceFactory(app=APP_METADATA)

    factory.update_kwargs("project", project_dir=in_project_path)
    factory.update_kwargs("provider", work_dir=in_project_path)
    factory.update_kwargs(
        "image", project_dir=in_project_path, work_dir=in_project_path
    )
    factory.update_kwargs(
        "lifecycle", work_dir=in_project_path, cache_dir=in_project_path / "cache"
    )

    # Mock out image info to avoid a umoci call requiring root privileges
    mocker.patch.object(
        services.RockcraftImageService,
        "_create_image_info",
        return_value=default_image_info,
    )

    return factory


@pytest.fixture
def configured_project(fake_services: ServiceFactory, fake_project_file) -> None:
    project_service = fake_services.get("project")
    project_service.configure(platform=None, build_for=None)


@pytest.fixture
def fake_app(fake_services: services.RockcraftServiceFactory) -> Rockcraft:
    from rockcraft.cli import fill_command_groups

    app = Rockcraft(app=APP_METADATA, services=fake_services)
    fill_command_groups(app)

    return app


@pytest.fixture
def fake_app_config(fake_app: Rockcraft) -> dict[str, Any]:
    return fake_app.app_config


@pytest.fixture
def fake_project_yaml(request: pytest.FixtureRequest):
    if "base" in request.fixturenames:
        base = request.getfixturevalue("base")
    else:
        base = craft_platforms.DistroBase.from_linux_distribution(
            distro.LinuxDistribution(
                include_lsb=False, include_uname=False, include_oslevel=False
            )
        )

    return DEFAULT_PROJECT_TEMPLATE.format(base=f"{base.distribution}@{base.series}")


@pytest.fixture
def fake_project_file(in_project_path, fake_project_yaml):
    project_file = in_project_path / "rockcraft.yaml"
    project_file.write_text(fake_project_yaml)

    return project_file
