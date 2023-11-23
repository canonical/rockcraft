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


def test_image_service_cache(image_service, default_image_info, mocker):
    """Test that the image service only creates the base image once."""
    mock_create = mocker.patch.object(
        image_service, "_create_image_info", return_value=default_image_info
    )

    info1 = image_service.obtain_image()
    info2 = image_service.obtain_image()

    assert info1 is default_image_info
    assert info2 is default_image_info

    mock_create.assert_called_once_with()
