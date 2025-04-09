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
from typing import cast

from craft_application import ServiceFactory
from rockcraft.services import RockcraftImageService, package


def test_pack(fake_services: ServiceFactory, default_image_info, mocker, rock_project):
    rock_project()
    image_service = cast(RockcraftImageService, fake_services.get("image"))

    mock_obtain_image = mocker.patch.object(
        image_service, "obtain_image", return_value=default_image_info
    )
    mock_inner_pack = mocker.patch.object(package, "_pack")

    fake_services.get("project").configure(platform="amd64", build_for="amd64")
    fake_services.get("package").pack(prime_dir=Path("prime"), dest=Path())

    # Check that the image service was queried for the ImageInfo
    mock_obtain_image.assert_called_once_with()

    # Check that the regular _pack() function was called with the correct
    # parameters.
    mock_inner_pack.assert_called_once_with(
        base_digest=b"deadbeef",
        base_layer_dir=Path(),
        build_for="amd64",
        prime_dir=Path("prime"),
        project=fake_services.get("project").get(),
        project_base_image=default_image_info.base_image,
        rock_suffix="amd64",
    )
