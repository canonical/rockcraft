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

from rockcraft.services import package


def test_pack(package_service, default_factory, default_image_info, mocker):
    image_service = default_factory.image

    mock_obtain_image = mocker.patch.object(
        image_service, "obtain_image", return_value=default_image_info
    )
    mock_inner_pack = mocker.patch.object(package, "_pack")

    package_service.pack(prime_dir=Path("prime"), dest=Path())

    # Check that the image service was queried for the ImageInfo
    mock_obtain_image.assert_called_once_with()

    # Check that the regular _pack() function was called with the correct
    # parameters.
    mock_inner_pack.assert_called_once_with(
        base_digest=b"deadbeef",
        base_layer_dir=Path(),
        build_for="amd64",
        prime_dir=Path("prime"),
        project=default_factory.project,
        project_base_image=default_image_info.base_image,
        rock_suffix="amd64",
    )
