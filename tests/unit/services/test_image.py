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

from rockcraft import oci
from rockcraft.services.image import ImageInfo


def test_image_service_cache(image_service, mocker):
    """Test that the image service only creates the base image once."""
    image_info = ImageInfo(
        base_image=oci.Image(image_name="fake_image", path=Path()),
        base_layer_dir=Path(),
        base_digest=b"deadbeef",
    )
    mock_create = mocker.patch.object(
        image_service, "_create_image_info", return_value=image_info
    )

    info1 = image_service.obtain_image()
    info2 = image_service.obtain_image()

    assert info1 is image_info
    assert info2 is image_info

    mock_create.assert_called_once_with()
