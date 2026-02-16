# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2022 Canonical Ltd.
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
import json
import os
import subprocess
import tarfile
import textwrap
from collections.abc import Callable
from pathlib import Path

import pytest
from rockcraft import oci
from rockcraft.services.image import ImageInfo

pytestmark = [
    pytest.mark.usefixtures("enable_overlay_feature"),
]


def create_base_image(
    work_dir: Path, populate_base_layer: Callable[[Path], None]
) -> tuple[oci.Image, Path]:
    """Create a base image with content provided by a callable.

    This function will create an empty image, extract it to a bundle and then
    call ``populate_base_layer(dir)`` to populate its rootfs. Then the image
    is repacked.

    :param work_dir: The directory where the image metadata should be stored
    :param populate_base_layer: A callable to create the desired filesystem
      structure for the image's sole layer.
    :return: The new image, and the path to the layer's extracted contents.
    """
    image_dir = work_dir / "images"
    image = oci.Image.new_oci_image(
        image_name="bare@original",
        image_dir=image_dir,
        arch="amd64",
    )[0]

    extracted_dir = work_dir / "extracted"
    base_layer_dir = image.extract_to(extracted_dir, rootless=True)
    assert base_layer_dir.is_dir()
    assert list(base_layer_dir.iterdir()) == []

    # Call the client function to populate the empty layer
    populate_base_layer(base_layer_dir)

    # Repack the image with the new contents overwriting the existing layer
    subprocess.check_output(
        [
            "umoci",
            "repack",
            "--image",
            f"{image_dir}/bare:original",
            f"{extracted_dir}/bare-original",
        ]
    )

    return image, base_layer_dir


def get_names_in_layer(image: oci.Image, layer_number: int = -1) -> list[str]:
    """Get the list of file/dir names contained in the given layer, sorted."""
    umoci_stat = image.stat()

    layers = umoci_stat["history"]
    new_layer = layers[layer_number]["layer"]
    assert new_layer["mediaType"] == "application/vnd.oci.image.layer.v1.tar+gzip"
    layer_basename = new_layer["digest"][len("sha256:") :]
    layer_file = Path(f"images/bare/blobs/sha256/{layer_basename}")

    with tarfile.open(layer_file, "r") as tar_file:
        return sorted(tar_file.getnames())


def test_add_layer_with_symlink_in_base(new_dir):
    """Test adding a new layer that conflicts with dir symlinks on the base (e.g. usrmerge)"""

    targets = ["lib", "bin"]

    def populate_base_layer(base_layer_dir):
        # Populate the "base" rootfs with some symlinks, in the following structure:
        # /bin -> usr/bin
        # /lib -> usr/lib
        # /usr/bin/old_bin_file
        # /usr/lib/old_lib_file
        for target in targets:
            actual_dir = base_layer_dir / f"usr/{target}"
            actual_dir.mkdir(parents=True)

            (actual_dir / f"old_{target}_file").write_text(f"old {target} file")

            (base_layer_dir / target).symlink_to(f"usr/{target}")
            assert os.listdir(base_layer_dir / target) == [f"old_{target}_file"]  # noqa: PTH208 (use Path.iterdir)

    image, base_layer_dir = create_base_image(Path(new_dir), populate_base_layer)

    new_layer_dir = Path("new")
    new_layer_dir.mkdir()

    for target in [*targets, "tmp"]:
        new_target_dir = new_layer_dir / target
        new_target_dir.mkdir()
        (new_target_dir / f"new_{target}_file").write_text(f"new {target} file")

    new_image = image.add_layer(
        tag="new", new_layer_dir=new_layer_dir, base_layer_dir=base_layer_dir
    )

    assert get_names_in_layer(new_image) == [
        "tmp",
        "tmp/new_tmp_file",
        "usr/bin/new_bin_file",
        "usr/lib/new_lib_file",
    ]


@pytest.mark.slow
@pytest.mark.usefixtures("fake_project_file", "project_keys")
@pytest.mark.parametrize(
    "project_keys",
    [
        {
            "parts": {
                "with-overlay": {
                    "plugin": "nil",
                    "override-build": "touch ${CRAFT_PART_INSTALL}/file_from_override_build",
                    "overlay-script": textwrap.dedent(
                        """
                cd ${CRAFT_OVERLAY}
                unlink bin
                mkdir bin
                touch bin/file_from_overlay_script
                """
                    ),
                }
            }
        }
    ],
)
def test_add_layer_with_overlay(new_dir, mocker, fake_services, mock_obtain_image):
    """Test "overwriting" directories in the base layer via overlays."""

    def populate_base_layer(base_layer_dir):
        (base_layer_dir / "usr/bin").mkdir(parents=True)
        (base_layer_dir / "bin").symlink_to("usr/bin")

    image, base_layer_dir = create_base_image(Path(new_dir), populate_base_layer)

    image_info = ImageInfo(
        base_image=image,
        base_layer_dir=base_layer_dir,
        base_digest=b"deadbeef",
    )
    mock_obtain_image.return_value = image_info

    # Mock os.geteuid() because currently craft-parts doesn't allow overlays
    # without superuser privileges.
    mock_geteuid = mocker.patch.object(os, "geteuid", return_value=0)

    fake_services.get("project").configure(build_for=None, platform=None)
    # Setup the service, to create the LifecycleManager.
    lifecycle_service = fake_services.get("lifecycle")
    assert mock_geteuid.called

    # Run the lifecycle.
    lifecycle_service.run("prime")

    new_image = image.add_layer(
        tag="new",
        new_layer_dir=lifecycle_service.prime_dir,
        base_layer_dir=base_layer_dir,
    )

    assert get_names_in_layer(new_image) == [
        "bin",
        "bin/.wh..wh..opq",
        "bin/file_from_overlay_script",
        "file_from_override_build",
        "usr",
        "usr/bin",
        "usr/bin/pebble",
        "var",
        "var/lib",
        "var/lib/pebble",
        "var/lib/pebble/default",
        "var/lib/pebble/default/layers",
    ]


def test_stat(new_dir):
    image = oci.Image.new_oci_image(
        image_name="bare@original",
        image_dir=Path("images"),
        arch="amd64",
    )[0]

    # Empty stat for an empty image
    stat = image.stat()
    assert stat == {"history": None}

    # Add a few layers and check the history
    layer1 = Path("layer1")
    layer1.mkdir()
    (layer1 / "file.txt").touch()
    layer1_image = image.add_layer("layer1", layer1)
    layer1_stat = layer1_image.stat()
    layer1_history = layer1_stat["history"]
    # Exactly 1 entry, for the 1 layer
    assert len(layer1_history) == 1

    layer2 = Path("layer2")
    layer2.mkdir()
    (layer2 / "file2.txt").touch()
    layer2_image = layer1_image.add_layer("layer2", layer2)
    layer2_stat = layer2_image.stat()
    layer2_history = layer2_stat["history"]
    assert len(layer2_history) == 2
    # The first layer in the ``layer2_history`` list is layer1
    assert layer2_history[0] == layer1_history[0]


@pytest.mark.usefixtures("new_dir")
def test_image_manifest_has_media_type():
    """Test that the image manifest has the correct media type."""
    image = oci.Image.new_oci_image(
        image_name="bare@original",
        image_dir=Path("images"),
        arch="amd64",
    )[0]

    # Check the media type of the manifest
    manifest = image.get_manifest()
    assert manifest["mediaType"] == "application/vnd.oci.image.manifest.v1+json"


@pytest.mark.parametrize(
    ("arch", "expected_arch", "expected_variant"),
    [
        ("armhf", "arm", "v7"),
        ("arm64", "arm64", "v8"),
        ("amd64", "amd64", None),
    ],
)
@pytest.mark.usefixtures("new_dir")
def test_image_manifest_has_arch_variant(arch, expected_arch, expected_variant):
    image = oci.Image.new_oci_image(
        image_name="bare@original",
        image_dir=Path("images"),
        arch=arch,
    )[0]

    image_path = image.path / image.image_name
    output: bytes = oci._process_run(  # pylint: disable=protected-access
        ["skopeo", "inspect", "--config", "--raw", f"oci:{str(image_path)}"]
    ).stdout
    config = json.loads(output)
    assert config["architecture"] == expected_arch
    assert config.get("variant") == expected_variant
