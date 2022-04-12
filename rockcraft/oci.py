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

from craft_cli import CraftError, emit

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
        image_dir.mkdir(parents=True, exist_ok=True)
        image_target = image_dir / image_name
        _copy_image(f"docker://{image_name}", f"oci:{image_target}")

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
        bundle_dir.mkdir(parents=True, exist_ok=True)
        bundle_path = bundle_dir / self.image_name.replace(":", "-")
        image_path = self.path / self.image_name
        shutil.rmtree(bundle_path, ignore_errors=True)
        _process_run(["umoci", "unpack", "--image", str(image_path), str(bundle_path)])

        return bundle_path / "rootfs"

    def add_layer(self, tag: str, layer_path: Path) -> "Image":
        """Add a layer to the image.

        :param tag: The tag of the image containing the new layer.
        :param layer_path: The path to the new layer root filesystem.
        """
        image_path = self.path / self.image_name

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
                            emit.trace(f"Adding to layer: {path}")
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

        name = self.image_name.split(":", 1)[0]
        return self.__class__(image_name=f"{name}:{tag}", path=self.path)

    def to_docker_daemon(self, tag: str) -> None:
        """Export the current image to the local docker daemon.

        :param tag: The tag to export.
        """
        name = self.image_name.split(":", 1)[0]
        src_path = self.path / f"{name}:{tag}"
        _copy_image(f"oci:{str(src_path)}", f"docker-daemon:{name}:{tag}")

    def to_oci_archive(self, tag: str, filename: str) -> None:
        """Export the current image to a tar archive in OCI format.

        :param tag: The tag to export.
        """
        name = self.image_name.split(":", 1)[0]
        src_path = self.path / f"{name}:{tag}"
        _copy_image(f"oci:{str(src_path)}", f"oci-archive:{filename}:{tag}")

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

    def set_entrypoint(self, entrypoint: List[str]) -> None:
        """Set the OCI image entrypoint.

        :param entrypoint: The default list of arguments to use as the command to
            execute when the container starts.
        """
        emit.progress("Configuring entrypoint...")
        image_path = self.path / self.image_name
        params = ["--clear=config.entrypoint"]
        for entry in entrypoint:
            params.extend(["--config.entrypoint", entry])
        _config_image(image_path, params)
        emit.message(f"Entrypoint set to {entrypoint}", intermediate=True)

    def set_cmd(self, cmd: List[str]) -> None:
        """Set the OCI image default command parameters.

        :param cmd: The default arguments to the entrypoint of the container. If
            entrypoint is not defined, the first entry of cmd is the executable to
            run when the container starts.
        """
        emit.progress("Configuring cmd...")
        image_path = self.path / self.image_name
        params = ["--clear=config.cmd"]
        for entry in cmd:
            params.extend(["--config.cmd", entry])
        _config_image(image_path, params)
        emit.message(f"Cmd set to {cmd}", intermediate=True)

    def set_env(self, env: List[str]) -> None:
        """Set the OCI image environment.

        :param env: A list of environment variables in ``NAME=VALUE`` format.
        """
        emit.progress("Configuring env...")
        image_path = self.path / self.image_name
        params = ["--clear=config.env"]
        for entry in env:
            params.extend(["--config.env", entry])
        _config_image(image_path, params)
        emit.message(f"Environment set to {env}", intermediate=True)


def _copy_image(source: str, destination: str) -> None:
    """Transfer images from source to destination."""
    _process_run(["skopeo", "--insecure-policy", "copy", source, destination])


def _config_image(image_path: Path, params: List[str]) -> None:
    """Configure the OCI image."""
    _process_run(["umoci", "config", "--image", str(image_path)] + params)


def _process_run(command: List[str], **kwargs) -> None:
    """Run a command and handle its output."""
    emit.trace(f"Execute process: {command!r}, kwargs={kwargs!r}")
    try:
        subprocess.run(
            command,
            **kwargs,
            capture_output=True,
            check=True,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as err:
        msg = f"Failed to copy image: {err!s}"
        if err.stderr:
            msg += f" ({err.stderr.strip()!s})"
        raise CraftError(msg) from err
