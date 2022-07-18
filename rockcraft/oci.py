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
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml
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

    @classmethod
    def new_oci_image(cls, image_name: str, image_dir: Path) -> "Image":
        """Create a new OCI image out of thin air.

        :param image_name: The image to initiate, in ``name:tag`` format.
        :param image_dir: The directory to store the local OCI image.

        :returns: The new image object.
        """
        image_dir.mkdir(parents=True, exist_ok=True)
        image_target = image_dir / image_name
        image_target_no_tag = str(image_target).split(":", maxsplit=1)[0]
        shutil.rmtree(image_target_no_tag, ignore_errors=True)
        _process_run(["umoci", "init", "--layout", image_target_no_tag])
        _process_run(["umoci", "new", "--image", str(image_target)])

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
            _compress_layer(layer_path, temp_file)
            _add_layer_into_image(str(image_path), str(temp_file), **{"--tag": tag})
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

    def set_env(self, env: List[Dict[str, str]]) -> None:
        """Set the OCI image environment.

        :param env: A list of dictionaries mapping environment variables to
            their values.
        """
        emit.progress("Configuring env...")
        image_path = self.path / self.image_name
        params = ["--clear=config.env"]
        env_list = []
        for entry in env:
            for name, value in entry.items():
                env_item = f"{name}={value}"
                env_list.append(env_item)
                params.extend(["--config.env", env_item])
        _config_image(image_path, params)
        emit.message(f"Environment set to {env_list}", intermediate=True)

    def set_control_data(self, metadata: Dict[str, Any]) -> None:
        """Create and populate the ROCK's control data folder.

        :param metadata: content for the ROCK's metadata YAML file
        :type metadata: Dict[str, Any]
        """
        emit.progress("Setting the ROCK's Control Data")
        local_control_data_path = Path(tempfile.mkdtemp())

        # the ROCK control data structure starts with the folder ".rock"
        control_data_rock_folder = local_control_data_path / ".rock"
        control_data_rock_folder.mkdir()

        rock_metadata_file = control_data_rock_folder / "metadata.yaml"
        with rock_metadata_file.open("w", encoding="utf-8") as rock_meta:
            yaml.dump(metadata, rock_meta)

        temp_tar_file = Path(self.path, f".temp_layer.control_data.{os.getpid()}.tar")
        temp_tar_file.unlink(missing_ok=True)

        try:
            _compress_layer(local_control_data_path, temp_tar_file)
            _add_layer_into_image(str(self.path / self.image_name), str(temp_tar_file))
        finally:
            temp_tar_file.unlink(missing_ok=True)

        emit.progress("Control data written")
        shutil.rmtree(local_control_data_path)

    def set_annotations(self, annotations: Dict[str, Any]) -> None:
        """Add the given annotations to the final image.

        :param annotations: A dictionary with each annotation/label and its value
        """
        emit.progress("Configuring labels and annotations...")
        image_path = self.path / self.image_name
        label_params = ["--clear=config.labels"]
        annotation_params = ["--clear=manifest.annotations"]

        labels_list = []
        for label_key, label_value in annotations.items():
            label_item = f"{label_key}={label_value}"
            labels_list.append(label_item)
            label_params.extend(["--config.label", label_item])
            annotation_params.extend(["--manifest.annotation", label_item])
        # Set the labels
        _config_image(image_path, label_params)
        # Set the annotations as a copy of these labels (for OCI compliance only)
        _config_image(image_path, annotation_params)
        emit.message(f"Labels and annotations set to {labels_list}", intermediate=True)


def _copy_image(source: str, destination: str) -> None:
    """Transfer images from source to destination."""
    # We need to preserve the digests when downloading the image
    # from the registry, otherwise a new one is generated and we
    # lose traceability
    _process_run(
        [
            "skopeo",
            "--insecure-policy",
            "copy",
            "--preserve-digests",
            source,
            destination,
        ]
    )


def _config_image(image_path: Path, params: List[str]) -> None:
    """Configure the OCI image."""
    _process_run(["umoci", "config", "--image", str(image_path)] + params)


def _add_layer_into_image(image_path: str, compressed_content: str, **kwargs) -> None:
    """Add raw layer (compressed) into the OCI image.

    :param image_path: path of the OCI image, in the format <image>:<tar>
    :type image_path: str
    :param compressed_content: path to the compressed content to be added
    :type compressed_content: str
    """
    cmd = ["umoci", "raw", "add-layer", "--image", image_path, compressed_content] + [
        arg_val for k, v in kwargs.items() for arg_val in [k, v]
    ]
    _process_run(cmd + ["--history.created_by", " ".join(cmd)])


def _compress_layer(layer_path: Path, temp_tar_file: Path) -> None:
    """Prepare new OCI layer by compressing its content into tar file.

    :param layer_path: path to the content to be compressed into a layer
    :type layer_path: Path
    :param temp_tar_file: path to the temporary tar fail holding the compressed content
    :type temp_tar_file: Path
    """
    old_dir = os.getcwd()
    try:
        os.chdir(layer_path)
        with tarfile.open(temp_tar_file, mode="w") as tar_file:
            for root, _, files in os.walk("."):
                for name in files:
                    path = os.path.join(root, name)
                    emit.trace(f"Adding to layer: {path}")
                    tar_file.add(path)
    finally:
        os.chdir(old_dir)


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
