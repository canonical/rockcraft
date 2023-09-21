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
from pathlib import Path
from unittest import mock

import pytest
from craft_parts import LifecycleManager, callbacks

from rockcraft.services import lifecycle as lifecycle_module

#  pylint: disable=protected-access


@pytest.fixture
def extra_project_params():
    return dict(package_repositories=[{"type": "apt", "ppa": "ppa/ppa"}])


def test_lifecycle_args(lifecycle_service, default_factory, default_image_info, mocker):
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
        base="ubuntu:22.04",
        base_layer_dir=Path("."),
        base_layer_hash=b"deadbeef",
        cache_dir=Path("cache"),
        ignore_local_sources=["*.rock"],
        package_repositories=[{"ppa": "ppa/ppa", "type": "apt"}],
        project_name="default",
        project_vars={"version": "1.0"},
        work_dir=Path("work"),
    )


def test_lifecycle_package_repositories(
    extra_project_params, lifecycle_service, default_project, mocker
):
    fake_repositories = extra_project_params["package_repositories"]
    lifecycle_service._lcm = mock.MagicMock(spec=LifecycleManager)

    # Installation of repositories in the build instance
    mock_install = mocker.patch.object(
        lifecycle_module, "_install_package_repositories"
    )
    # Installation of repositories in overlays
    mock_callback = mocker.patch.object(callbacks, "register_configure_overlay")

    lifecycle_service.run("prime")

    mock_install.assert_called_once_with(fake_repositories, lifecycle_service._lcm)
    mock_callback.assert_called_once_with(
        lifecycle_module._install_overlay_repositories
    )
