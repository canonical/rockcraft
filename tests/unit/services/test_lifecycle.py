# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
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
from unittest import mock

import pytest
from craft_application import util
from craft_application.util import repositories
from craft_parts import (
    LifecycleManager,
    Part,
    PartInfo,
    ProjectDirs,
    ProjectInfo,
    Step,
    StepInfo,
    callbacks,
)
from craft_parts.state_manager.prime_state import PrimeState

from rockcraft.services import lifecycle as lifecycle_module

#  pylint: disable=protected-access


@pytest.fixture()
def extra_project_params():
    return {"package_repositories": [{"type": "apt", "ppa": "ppa/ppa"}]}


def test_lifecycle_args(
    lifecycle_service, default_factory, default_image_info, mocker, monkeypatch
):
    monkeypatch.setenv("CRAFT_PARALLEL_BUILD_COUNT", "4")
    image_service = default_factory.image

    mock_obtain_image = mocker.patch.object(
        image_service, "obtain_image", return_value=default_image_info
    )
    mock_lifecycle = mocker.patch.object(
        LifecycleManager, "__init__", return_value=None
    )

    lifecycle_service.setup()

    mock_obtain_image.assert_called_once_with()
    mock_lifecycle.assert_called_once_with(
        {"parts": {}},
        application_name="rockcraft",
        arch="x86_64",
        base="ubuntu@22.04",
        base_layer_dir=Path(),
        base_layer_hash=b"deadbeef",
        cache_dir=Path("cache"),
        ignore_local_sources=["*.rock"],
        package_repositories=[{"ppa": "ppa/ppa", "type": "apt"}],
        parallel_build_count=4,
        partitions=None,
        project_name="default",
        project_vars={"version": "1.0"},
        project_vars_part_name=None,
        work_dir=Path("work"),
        rootfs_dir=Path("."),
        track_stage_packages=True,
    )


def test_lifecycle_package_repositories(
    extra_project_params, lifecycle_service, default_project, mocker, default_build_plan
):
    base = default_build_plan[0].base
    mocker.patch.object(util, "get_host_base", return_value=base)
    fake_repositories = extra_project_params["package_repositories"]
    lifecycle_service._lcm = mock.MagicMock(spec=LifecycleManager)

    # Installation of repositories in the build instance
    mock_install = mocker.patch.object(repositories, "install_package_repositories")
    # Installation of repositories in overlays
    mock_callback = mocker.patch.object(callbacks, "register_configure_overlay")

    lifecycle_service.run("prime")

    mock_install.assert_called_once_with(fake_repositories, lifecycle_service._lcm)
    mock_callback.assert_called_once_with(repositories.install_overlay_repositories)


def test_python_usrmerge_fix(tmp_path):
    # The test setup is rather involved because we need to recreate/mock an
    # exact set of circumstances here:

    # 1) Create a project with 24.04 base;
    dirs = ProjectDirs(work_dir=tmp_path)
    project_info = ProjectInfo(
        project_dirs=dirs,
        application_name="test",
        cache_dir=tmp_path,
        strict_mode=False,
        base="ubuntu@24.04",
    )

    # 2) Create a part using the Python plugin;
    part = Part("p1", {"source": ".", "plugin": "python"})
    part_info = PartInfo(project_info=project_info, part=part)

    prime_dir = dirs.prime_dir
    prime_dir.mkdir()

    # 3) Setup a 'prime' directory where "lib64" is a symlink to "lib";
    (prime_dir / "lib").mkdir()
    (prime_dir / "lib64").symlink_to("lib")

    # 4) Create a StepInfo that contains all of this.
    step_info = StepInfo(part_info=part_info, step=Step.PRIME)
    step_info.state = PrimeState(part_properties=part.spec.marshal(), files={"lib64"})

    assert sorted(os.listdir(prime_dir)) == ["lib", "lib64"]

    lifecycle_module._python_usrmerge_fix(step_info)

    # After running the fix the "lib64" symlink must be gone
    assert sorted(os.listdir(prime_dir)) == ["lib"]
