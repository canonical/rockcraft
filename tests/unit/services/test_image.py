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

from types import SimpleNamespace
from typing import cast

import pytest
from rockcraft import oci
from rockcraft.services import RockcraftImageService


def test_image_service_cache(default_image_info, mocker, fake_services):
    """Test that the image service only creates the base image once."""
    image_service = cast(RockcraftImageService, fake_services.get("image"))
    mock_create = mocker.patch.object(
        image_service, "_create_image_info", return_value=default_image_info
    )

    info1 = image_service.obtain_image()
    info2 = image_service.obtain_image()

    assert info1 is default_image_info
    assert info2 is default_image_info

    mock_create.assert_called_once_with()


@pytest.mark.parametrize(
    ("registry_url", "expected_registry_url"),
    [
        ("https://registry.example:5000/cache", "https://registry.example:5000/cache"),
        (None, oci.DEFAULT_REGISTRY_URL),
    ],
)
def test_image_service_passes_configured_registry_to_oci(
    registry_url, expected_registry_url, mocker, tmp_path, monkeypatch
):
    """The image service passes the configured registry to OCI image retrieval."""
    if registry_url is None:
        monkeypatch.delenv("ROCKCRAFT_BASE_IMAGE_REGISTRY_URL", raising=False)
    else:
        monkeypatch.setenv("ROCKCRAFT_BASE_IMAGE_REGISTRY_URL", registry_url)

    build_plan = mocker.Mock()
    build_plan.plan.return_value = [SimpleNamespace(build_for="amd64")]
    project = mocker.Mock()
    project.get.return_value = SimpleNamespace(base="ubuntu@22.04", name="test")
    services = mocker.Mock()
    services.get.side_effect = {
        "build_plan": build_plan,
        "project": project,
    }.get

    base_image = mocker.Mock(spec=oci.Image)
    base_image.image_name = "ubuntu:22.04"
    base_image.extract_to.return_value = tmp_path / "bundle"
    project_base_image = mocker.Mock(spec=oci.Image)
    base_image.copy_to.return_value = project_base_image
    project_base_image.digest.return_value = b"digest"
    from_registry = mocker.patch.object(
        oci.Image,
        "from_docker_registry",
        return_value=(base_image, "docker://registry/ubuntu:22.04"),
    )
    mocker.patch("rockcraft.services.image.emit.progress")

    image_service = RockcraftImageService(
        mocker.Mock(), services, project_dir=tmp_path, work_dir=tmp_path
    )
    image_service._create_image_info()

    from_registry.assert_called_once_with(
        "ubuntu@22.04",
        image_dir=tmp_path / "images",
        arch="amd64",
        registry_url=expected_registry_url,
    )
