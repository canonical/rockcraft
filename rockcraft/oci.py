# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021 Canonical Ltd.
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

"""OCI image manipulation helpers."""


import logging
import os
import shutil
import subprocess
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import List

from rockcraft import ui

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Image:
    """A local OCI image.

    :param image_name: The name of this image in ``name:tag`` format.
    :param path: The path to this image in the local filesystem.
    """

    image_name: str
    path: Path

    @classmethod
    def from_docker_registry(cls, image_name: str, *, image_dir: Path) -> "Image":
        """Obtain an image from a docker registry.

        :param image_name: The image to retrieve, in ``name:tag`` format.
        :param image_dir: The directory to store local OCI images.

        :returns: The downloaded image.
        """
        ui.emit.progress(f"Retrieving base {image_name}")

        image_dir.mkdir(parents=True, exist_ok=True)
        image_target = image_dir / image_name
        _copy_image(f"docker://{image_name}", f"oci:{image_target}")

        ui.emit.message(f"Retrieved base {image_name}")

        return cls(image_name=image_name, path=image_dir)

    def copy_to(self, image_name: str, *, image_dir: Path) -> "Image":
        """Make a copy of the current image.

        :param image_name: The new image name, in ``name:tag`` format.
        :param image_dir: The new image directory.

        :returns: The newly created image.
        """
        src_path = self.path / self.image_name
        dest_path = image_dir / image_name
        _copy_image(f"oci:{str(src_path)}", f"oci:{str(dest_path)}")

        return Image(image_name=image_name, path=image_dir)

    def extract_to(self, bundle_dir: Path) -> Path:
        """Unpack the image to an OCI runtime bundle.

        :param bundle_dir: The directory to store runtime bundles.
        """
        ui.emit.progress(f"Extracting {self.image_name}")

        bundle_dir.mkdir(parents=True, exist_ok=True)
        bundle_path = bundle_dir / self.image_name.replace(":", "-")
        image_path = self.path / self.image_name
        shutil.rmtree(bundle_path, ignore_errors=True)
        _process_run(["umoci", "unpack", "--image", str(image_path), str(bundle_path)])

        ui.emit.message(f"Extracted {self.image_name}")

        return bundle_path / "rootfs"

    def add_layer(self, tag: str, layer_path: Path) -> None:
        """Add a layer to the image.

        :param tag: The tag of the image containing the new layer.
        :param layer_path: The path to the new layer root filesystem.
        """
        image_path = self.path / self.image_name

        ui.emit.progress("Creating new layer")

        temp_file = Path(self.path, f".temp_layer.{os.getpid()}.tar")
        temp_file.unlink(missing_ok=True)

        try:
            old_dir = os.getcwd()
            try:
                os.chdir(layer_path)
                with tarfile.open(temp_file, mode="w") as tar_file:
                    for root, _, files in os.walk("."):
                        for name in files:
                            path = os.path.join(root, name)
                            ui.emit.trace(f"Adding to layer: {path}")
                            tar_file.add(path)
            finally:
                os.chdir(old_dir)

            _process_run(
                [
                    "umoci",
                    "raw",
                    "add-layer",
                    "--tag",
                    tag,
                    "--image",
                    str(image_path),
                    str(temp_file),
                ]
            )
        finally:
            temp_file.unlink(missing_ok=True)

        ui.emit.message("Created new layer")

    def to_docker_daemon(self, tag: str) -> None:
        """Export the current image to the local docker daemon.

        :param tag: The tag to export.
        """
        parts = self.image_name.split(":", 1)
        name = parts[0]

        ui.emit.progress(f"Exporting {name}:{tag} to local docker daemon")

        src_path = self.path / f"{name}:{tag}"
        _copy_image(f"oci:{str(src_path)}", f"docker-daemon:{name}:{tag}")

        ui.emit.message(f"Exported {name}:{tag} to local docker daemon")

    def digest(self) -> bytes:
        """Obtain the current image digest.

        :returns: The image digest bytes.
        """
        image_path = self.path / self.image_name
        output = subprocess.check_output(
            ["skopeo", "inspect", "--format", "{{.Digest}}", f"oci:{str(image_path)}"],
            text=True,
        )
        parts = output.split(":", 1)
        return bytes.fromhex(parts[-1])


def _copy_image(source: str, destination: str) -> None:
    """Transfer images from source to destination."""
    _process_run(["skopeo", "--insecure-policy", "copy", source, destination])


# XXX: update to use craft-cli output stream
def _process_run(command: List[str], **kwargs) -> None:
    """Run a command and handle its output."""
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        **kwargs,
    ) as proc:
        if not proc.stdout:
            return
        for line in iter(proc.stdout.readline, ""):
            logger.info(":: %s", line.strip())
        ret = proc.wait()

    if ret:
        raise subprocess.CalledProcessError(ret, command)
