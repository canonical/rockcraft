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
import os
import subprocess
import tarfile
from pathlib import Path

from rockcraft import oci
from tests.util import jammy_only

pytestmark = jammy_only


def test_add_layer_with_symlink_in_base(new_dir):
    """Test adding a new layer that conflicts with dir symlinks on the base (e.g. usrmerge)"""
    image = oci.Image.new_oci_image(
        image_name="bare:original",
        image_dir=Path("images"),
        arch="amd64",
    )[0]

    rootfs = image.extract_to(Path("bundle"), rootless=True)

    # Make sure the rootfs is empty
    assert rootfs.is_dir()
    assert os.listdir(rootfs) == []

    targets = ["lib", "bin"]

    # Populate the "base" rootfs with some symlinks, in the following structure:
    # /bin -> usr/bin
    # /lib -> usr/lib
    # /usr/bin/old_bin_file
    # /usr/lib/old_lib_file
    for target in targets:
        actual_dir = rootfs / f"usr/{target}"
        actual_dir.mkdir(parents=True)

        (actual_dir / f"old_{target}_file").write_text(f"old {target} file")

        os.symlink(f"usr/{target}", rootfs / target)
        assert os.listdir(rootfs / target) == [f"old_{target}_file"]

    # Repack the image with the new contents overwriting the existing layer
    subprocess.check_output(
        ["umoci", "repack", "--image", "images/bare:original", "bundle/bare-original"]
    )

    new_layer_dir = Path("new")
    new_layer_dir.mkdir()

    # Create the following structure to use as a new layer:
    # /bin/new_bin_file
    # /lib/new_lib_file
    # /tmp/new_tmp_file
    for target in targets + ["tmp"]:
        new_target_dir = new_layer_dir / target
        new_target_dir.mkdir()
        (new_target_dir / f"new_{target}_file").write_text(f"new {target} file")

    new_image = image.add_layer(
        tag="new", layer_path=new_layer_dir, lower_rootfs=rootfs
    )

    umoci_stat = new_image.stat()

    layers = umoci_stat["history"]
    assert len(layers) == 2
    new_layer = layers[1]["layer"]
    assert new_layer["mediaType"] == "application/vnd.oci.image.layer.v1.tar+gzip"
    layer_basename = new_layer["digest"][len("sha256:") :]
    layer_file = Path(f"images/bare/blobs/sha256/{layer_basename}")

    # Check that the files were added into the symlink targets.
    with tarfile.open(layer_file, "r") as tar_file:
        assert sorted(tar_file.getnames()) == [
            "./tmp",
            "./tmp/new_tmp_file",
            "./usr/bin/new_bin_file",
            "./usr/lib/new_lib_file",
        ]


def test_stat(new_dir):
    image = oci.Image.new_oci_image(
        image_name="bare:original",
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
