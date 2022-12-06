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

import hashlib
import json
import logging
import os
import shutil
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
    def from_docker_registry(
        cls,
        image_name: str,
        *,
        image_dir: Path,
        arch: str,
        variant: Optional[str] = None,
    ) -> Tuple["Image", str]:
        """Obtain an image from a docker registry.

        :param image_name: The image to retrieve, in ``name:tag`` format.
        :param image_dir: The directory to store local OCI images.
        :param arch: The architecture of the Docker image to fetch.
        :param variant: The variant, if any, of the Docker image to fetch.


        :returns: The downloaded image and it's corresponding source image
        """
        image_dir.mkdir(parents=True, exist_ok=True)
        image_target = image_dir / image_name

        source_image = f"docker://{image_name}"
        platform_params = ["--override-arch", arch]
        if variant:
            platform_params += ["--override-variant", variant]
        _copy_image(source_image, f"oci:{image_target}", *platform_params)

        return cls(image_name=image_name, path=image_dir), source_image

    @classmethod
    def new_oci_image(
        cls, image_name: str, image_dir: Path, arch: str, variant: Optional[str] = None
    ) -> Tuple["Image", str]:
        """Create a new OCI image out of thin air.

        :param image_name: The image to initiate, in ``name:tag`` format.
        :param image_dir: The directory to store the local OCI image.
        :param arch: The architecture of the OCI image to create.
        :param variant: The variant, if any, of the OCI image to create.

        :returns: The new image object and it's corresponding source image
        """
        image_dir.mkdir(parents=True, exist_ok=True)
        image_target = image_dir / image_name
        image_target_no_tag = str(image_target).split(":", maxsplit=1)[0]
        shutil.rmtree(image_target_no_tag, ignore_errors=True)
        _process_run(["umoci", "init", "--layout", image_target_no_tag])
        _process_run(["umoci", "new", "--image", str(image_target)])

        # Unfortunately, umoci does not allow initializing an image
        # with arch and variant. We can configure the arch via
        # umoci config, but not the variant. Need to do it manually
        _config_image(image_target, ["--architecture", arch, "--no-history"])
        if variant:
            _inject_architecture_variant(Path(image_target_no_tag), variant)

        # for new OCI images, the source image corresponds to the newly generated image
        return cls(image_name=image_name, path=image_dir), f"oci:{str(image_target)}"

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

    def extract_to(self, bundle_dir: Path, *, rootless: bool = False) -> Path:
        """Unpack the image to an OCI runtime bundle.

        :param bundle_dir: The directory to store runtime bundles.
        :param rootless: Whether the image should be unpacked even without
            root; won't necessarily preserve ownership but is useful for
            testing.
        """
        bundle_dir.mkdir(parents=True, exist_ok=True)
        bundle_path = bundle_dir / self.image_name.replace(":", "-")
        image_path = self.path / self.image_name
        shutil.rmtree(bundle_path, ignore_errors=True)
        command = ["umoci", "unpack"]
        if rootless:
            command.append("--rootless")
        command.extend(["--image", str(image_path), str(bundle_path)])
        _process_run(command)

        return bundle_path / "rootfs"

    def add_layer(
        self, tag: str, new_layer_dir: Path, base_layer_dir: Optional[Path] = None
    ) -> "Image":
        """Add a layer to the image.

        :param tag: The tag of the image containing the new layer.
        :param new_layer_dir: The path to the new layer root filesystem.
        :param base_layer_dir: An optional path to the extracted contents of the
          new layer's base layer. Used to preserve lower-layer symlinks.
        """
        image_path = self.path / self.image_name

        temp_file = Path(self.path, f".temp_layer.{os.getpid()}.tar")
        temp_file.unlink(missing_ok=True)

        try:
            _archive_layer(new_layer_dir, temp_file, base_layer_dir)
            _add_layer_into_image(image_path, temp_file, **{"--tag": tag})
        finally:
            temp_file.unlink(missing_ok=True)

        name = self.image_name.split(":", 1)[0]
        return self.__class__(image_name=f"{name}:{tag}", path=self.path)

    def stat(self) -> Dict[Any, Any]:
        """Obtain the image statistics, as reported by "umoci stat --json"."""
        image_path = self.path / self.image_name
        output = _process_run(
            ["umoci", "stat", "--json", "--image", str(image_path)]
        ).stdout
        return json.loads(output)

    @staticmethod
    def digest(source_image: str) -> bytes:
        """Obtain the image digest, given its full form name {transport}:{name}.

        :param source_image: the source image name, it its full form (e.g. docker://ubuntu:22.04)
        :returns: The image digest bytes.
        """
        output = subprocess.check_output(
            ["skopeo", "inspect", "--format", "{{.Digest}}", "-n", source_image],
            text=True,
        )
        parts = output.split(":", 1)
        return bytes.fromhex(parts[-1])

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
        emit.progress(f"Entrypoint set to {entrypoint}", permanent=True)

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
        emit.progress(f"Cmd set to {cmd}", permanent=True)

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
        emit.progress(f"Environment set to {env_list}", permanent=True)

    def set_control_data(self, metadata: Dict[str, Any]) -> None:
        """Create and populate the ROCK's control data folder.

        :param metadata: content for the ROCK's metadata YAML file
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
            _archive_layer(local_control_data_path, temp_tar_file)
            _add_layer_into_image(self.path / self.image_name, temp_tar_file)
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
        emit.progress(f"Labels and annotations set to {labels_list}", permanent=True)


def _copy_image(source: str, destination: str, *system_params) -> None:
    """Transfer images from source to destination."""
    _process_run(
        [
            "skopeo",
            "--insecure-policy",
        ]
        + list(system_params)
        + [
            "copy",
            source,
            destination,
        ]
    )


def _config_image(image_path: Path, params: List[str]) -> None:
    """Configure the OCI image."""
    _process_run(["umoci", "config", "--image", str(image_path)] + params)


def _add_layer_into_image(image_path: Path, archived_content: Path, **kwargs) -> None:
    """Add raw layer (archived) into the OCI image.

    :param image_path: path of the OCI image, in the format <image>:<tar>
    :param archived_content: path to the archived content to be added
    """
    cmd = [
        "umoci",
        "raw",
        "add-layer",
        "--image",
        str(image_path),
        str(archived_content),
    ] + [arg_val for k, v in kwargs.items() for arg_val in [k, v]]
    _process_run(cmd + ["--history.created_by", " ".join(cmd)])


def _archive_layer(
    new_layer_dir: Path, temp_tar_file: Path, base_layer_dir: Optional[Path] = None
) -> None:
    """Prepare new OCI layer by archiving its content into tar file.

    :param new_layer_dir: path to the content to be archived into a layer
    :param temp_tar_file: path to the temporary tar file holding the archived content
    :param base_layer_dir: optional path to the filesystem containing the extracted
        base below this new layer. Used to preserve lower-level directory symlinks,
        like the ones from Debian/Ubuntu's usrmerge.
    """
    with tarfile.open(temp_tar_file, mode="w") as tar_file:
        for dirpath, subdirs, filenames in os.walk(new_layer_dir):
            # Sort `subdirs` in-place, to ensure that `os.walk()` iterates on
            # them in sorted order.
            subdirs.sort()

            upper_subpath = Path(dirpath)
            lower_symlink_target: Optional[Path] = None

            # Handle adding an entry for the directory. We only do that if:
            # - The directory is not the root (to skip a spurious "." entry);
            # - The directory's name does not exist on ``lower_rootfs`` as a symlink
            #   to another directory (like in usrmerge).
            if upper_subpath != new_layer_dir:
                add_dir = True
                relative_path = upper_subpath.relative_to(new_layer_dir)

                if base_layer_dir is not None:
                    lower_path = base_layer_dir / relative_path
                    emit.debug(
                        f"Skipping {upper_subpath} because it exists as a symlink on the lower layer"
                    )
                    add_dir = not lower_path.is_symlink()
                    if lower_path.is_symlink():
                        lower_symlink_target = Path(os.readlink(lower_path))

                if add_dir:
                    emit.debug(f"Adding to layer: {upper_subpath}")
                    tar_file.add(
                        upper_subpath, arcname=f"{relative_path}", recursive=False
                    )

            # Handle adding each file in the directory.
            for name in filenames:
                path = upper_subpath / name
                if lower_symlink_target is not None:
                    # If the directory containing `name` is a symlink on the lower
                    # layer, add `name` into the symlink's target instead.
                    # For example: if the file is `bin/file.txt`, and `bin` is a
                    # symlink to `usr/bin`, add the file as `usr/bin/file.txt`.
                    relative_path = lower_symlink_target / name
                else:
                    relative_path = Path(path).relative_to(new_layer_dir)
                emit.debug(f"Adding to layer: {path}")
                tar_file.add(path, arcname=f"{relative_path}")


def _inject_architecture_variant(image_path: Path, variant: str) -> None:
    """Inject architecture variant into existing OCI Image config.

    :param image_path: path of the OCI image, in the format <image>:<tar>
    :param variant: name of the variant to inject in the OCI config
    """
    # pylint: disable=too-many-locals
    blobs_path = image_path / "blobs" / "sha256"
    # Get the top level OCI index
    tl_index_path = image_path / "index.json"
    tl_index = json.loads(tl_index_path.read_bytes())

    # Since this is a 1-arch OCI image, the OCI top level index
    # points to a manifest (otherwise it would be a manifest list)
    manifest_digest = tl_index["manifests"][0]["digest"].split(":")[-1]
    manifest_path = blobs_path / manifest_digest
    manifest_content = json.loads(manifest_path.read_bytes())

    # Get the current OCI Image Config
    image_config_digest = manifest_content["config"]["digest"].split(":")[-1]
    image_config_path = blobs_path / image_config_digest
    image_config_content = json.loads(image_config_path.read_bytes())

    # Set the variant
    image_config_content["variant"] = variant

    # The OCI image config has changed, so now we need to
    # regenerate the digests
    new_image_config_bytes = json.dumps(image_config_content).encode("utf-8")
    new_image_config_digest = hashlib.sha256(new_image_config_bytes).hexdigest()
    new_image_config_path = blobs_path / new_image_config_digest
    new_image_config_path.write_bytes(new_image_config_bytes)

    manifest_content["config"]["digest"] = f"sha256:{new_image_config_digest}"
    manifest_content["config"]["size"] = len(new_image_config_bytes)

    new_manifest_bytes = json.dumps(manifest_content).encode("utf-8")
    new_manifest_digest = hashlib.sha256(new_manifest_bytes).hexdigest()
    new_manifest_path = blobs_path / new_manifest_digest
    new_manifest_path.write_bytes(new_manifest_bytes)

    tl_index["manifests"][0]["digest"] = f"sha256:{new_manifest_digest}"
    tl_index["manifests"][0]["size"] = len(new_manifest_bytes)
    tl_index_path.write_bytes(json.dumps(tl_index).encode("utf-8"))


def _process_run(command: List[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command and handle its output."""
    emit.trace(f"Execute process: {command!r}, kwargs={kwargs!r}")
    try:
        return subprocess.run(
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
