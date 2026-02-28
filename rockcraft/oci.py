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
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml
from craft_cli import emit

from rockcraft import errors, layers
from rockcraft.architectures import SUPPORTED_ARCHS
from rockcraft.constants import ROCK_CONTROL_DIR
from rockcraft.pebble import Pebble
from rockcraft.utils import get_snap_command_path

logger = logging.getLogger(__name__)

# Public Amazon Elastic Container Registry has images that are updated more frequently
# and with less severe pull-rate limits than Docker Hub.
ECR_URL = "public.ecr.aws/ubuntu"

REGISTRY_URL = ECR_URL

# The number of times to try downloading an image from `REGISTRY_URL`.
MAX_DOWNLOAD_RETRIES = 5

MANIFEST_MEDIA_TYPE = "application/vnd.oci.image.manifest.v1+json"


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
    ) -> tuple["Image", str]:
        """Obtain an image from a docker registry.

        The image is fetched from the registry at ``REGISTRY_URL``.

        :param image_name: The image to retrieve, in ``name@tag`` format.
        :param image_dir: The directory to store local OCI images.
        :param arch: The architecture of the Docker image to fetch, in Debian format.
        :param variant: The variant, if any, of the Docker image to fetch.


        :returns: The downloaded image and it's corresponding source image
        """
        if "@" not in image_name:
            raise ValueError(f"Bad image name: {image_name}")

        image_name = image_name.replace("@", ":")

        image_dir.mkdir(parents=True, exist_ok=True)
        image_target = image_dir / image_name

        source_image = f"docker://{REGISTRY_URL}/{image_name}"
        copy_params = ["--retry-times", str(MAX_DOWNLOAD_RETRIES)]

        mapping = SUPPORTED_ARCHS[arch]

        platform_params = [
            "--override-arch",
            mapping.go_arch,
        ]
        if mapping.go_variant:
            platform_params += ["--override-variant", mapping.go_variant]

        _copy_image(
            source_image,
            f"oci:{image_target}",
            *platform_params,
            copy_params=copy_params,
        )

        return cls(image_name=image_name, path=image_dir), source_image

    @classmethod
    def new_oci_image(
        cls,
        image_name: str,
        image_dir: Path,
        arch: str,
    ) -> tuple["Image", str]:
        """Create a new OCI image out of thin air.

        :param image_name: The image to initiate, in ``name@tag`` format.
        :param image_dir: The directory to store the local OCI image.
        :param arch: The architecture of the OCI image to create, in Debian format.
        :param variant: The variant, if any, of the OCI image to create.

        :returns: The new image object and it's corresponding source image
        """
        if "@" not in image_name:
            raise ValueError(f"Bad image name: {image_name}")

        image_name = image_name.replace("@", ":")
        image_dir.mkdir(parents=True, exist_ok=True)
        image_target = image_dir / image_name
        image_target_no_tag = str(image_target).split(":", maxsplit=1)[0]

        shutil.rmtree(image_target_no_tag, ignore_errors=True)
        _process_run(["umoci", "init", "--layout", image_target_no_tag])
        _process_run(["umoci", "new", "--image", str(image_target)])

        # Note: umoci's docs aren't clear on this but we assume that arch-related
        # calls must use GOARCH-format, following the OCI spec.
        mapping = SUPPORTED_ARCHS[arch]

        # Unfortunately, umoci does not allow initializing an image
        # with arch and variant. We can configure the arch via
        # umoci config, but not the variant. Need to do it manually
        _config_image(image_target, ["--architecture", mapping.go_arch, "--no-history"])

        _inject_oci_fields(
            image_target,
            arch_variant=mapping.go_variant,
        )

        # for new OCI images, the source image corresponds to the newly generated image
        return (
            cls(image_name=image_name, path=image_dir),
            f"oci:{str(image_target)}",
        )

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
        self,
        tag: str,
        new_layer_dir: Path,
        base_layer_dir: Path | None = None,
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
            layers.archive_layer(new_layer_dir, temp_file, base_layer_dir)
            _add_layer_into_image(image_path, temp_file, **{"--tag": tag})
        finally:
            temp_file.unlink(missing_ok=True)

        name = self.image_name.split(":", 1)[0]
        return self.__class__(image_name=f"{name}:{tag}", path=self.path)

    def add_user(
        self,
        prime_dir: Path,
        base_layer_dir: Path,
        tag: str,
        username: str,
        uid: int,
    ) -> None:
        """Create a new rock user.

        :param prime_dir: Path to the user-defined parts' primed content.
        :param base_layer_dir: Path to the base layer's root filesystem.
        :param tag: The rock's image tag.
        :param username: Username to be created. Same as group name.
        :param uid: UID of the username to be created. Same as GID.
        """
        # pylint: disable=too-many-arguments
        user_files = {"passwd": "", "group": "", "shadow": ""}

        prime_dir_etc = prime_dir / "etc"
        base_layer_dir_etc = base_layer_dir / "etc"
        # Being cautious about possible changes (edits or removals) in
        # /etc/{passwd,group,shadow} done by the user through overlay scripts.
        # Basically:
        #  - if it exists in prime, use it,
        #  - if it doesn't exist in prime AND isn't "whiteout", use the base,
        #  - if it is "whiteout" or doesn't exist anywhere, use an empty file.
        # NOTE: "shadow" is only modified if it already exists.
        for u_file in user_files:
            if (prime_dir_etc / u_file).exists():
                user_files[u_file] = (prime_dir_etc / u_file).read_text()
            elif (base_layer_dir_etc / u_file).exists() and not (
                prime_dir_etc / f".wh.{u_file}"
            ).exists():
                user_files[u_file] = (base_layer_dir_etc / u_file).read_text()

        if (  # pylint: disable=too-many-boolean-expressions
            f"\n{username}:" in user_files["passwd"]
            or user_files["passwd"].startswith(f"{username}:")
            or f":{uid}:" in user_files["passwd"]
            or f"\n{username}:" in user_files["group"]
            or user_files["group"].startswith(f"{username}:")
            or f":{uid}:" in user_files["group"]
        ):
            raise errors.RockcraftError(
                str(
                    f"Error while trying to create user {username}:{uid}, "
                    f"with group {username}:{uid}...\n"
                    " - conflict with existing user/group in the base filesystem"
                )
            )

        user_files["passwd"] += (
            f"{username}:x:{uid}:{uid}::/{Pebble.PEBBLE_PATH}:/usr/bin/false\n"
        )
        user_files["group"] += f"{username}:x:{uid}:\n"

        with tempfile.TemporaryDirectory() as tmpfs:
            tmpfs_etc = Path(tmpfs) / "etc"
            tmpfs_etc.mkdir(parents=True, exist_ok=True)
            with (tmpfs_etc / "passwd").open("a+") as passwdf:
                passwdf.write(user_files["passwd"])

            with (tmpfs_etc / "group").open("a+") as groupf:
                groupf.write(user_files["group"])

            if user_files["shadow"]:
                days_since_epoch = (datetime.utcnow() - datetime(1970, 1, 1)).days  # type: ignore[reportDeprecated]

                # only add the shadow file if there's already one in the base image
                with (tmpfs_etc / "shadow").open("a+") as shadowf:
                    shadowf.write(
                        user_files["shadow"]
                        + f"{username}:!:{days_since_epoch}::::::\n"
                    )

            emit.progress(f"Adding user {username}:{uid} with group {username}:{uid}")
            self.add_layer(tag, Path(tmpfs))

    def stat(self) -> dict[str, Any]:
        """Obtain the image statistics, as reported by "umoci stat --json"."""
        image_path = self.path / self.image_name
        output: bytes = _process_run(
            ["umoci", "stat", "--json", "--image", str(image_path)]
        ).stdout
        result: dict[str, Any] = json.loads(output)
        return result

    def get_manifest(self) -> dict[str, Any]:
        """Obtain the image manifest, as reported by "skopeo inspect --raw"."""
        image_path = self.path / self.image_name
        output: bytes = _process_run(
            ["skopeo", "inspect", "--raw", f"oci:{str(image_path)}"]
        ).stdout
        result: dict[str, Any] = json.loads(output)
        return result

    @staticmethod
    def digest(source_image: str) -> bytes:
        """Obtain the image digest, given its full form name {transport}:{name}.

        :param source_image: the source image name, it its full form (e.g. docker://ubuntu:22.04)
        :returns: The image digest bytes.
        """
        output = subprocess.check_output(
            [
                get_snap_command_path("skopeo"),
                "inspect",
                "--format",
                "{{.Digest}}",
                "-n",
                source_image,
            ],
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

    def set_default_user(self, userid: int, username: str) -> None:
        """Set the default runtime user for the OCI image.

        :param userid: userid of the default user (must already exist)
        :param username: username of the default user (must already exist)
        """
        image_path = self.path / self.image_name
        params = ["--clear=config.entrypoint", "--config.user", str(userid)]
        _config_image(image_path, params)
        emit.progress(f"Default user set to {userid} ({username})")

    def set_entrypoint(self, entrypoint: list[str]) -> None:
        """Set the OCI image entrypoint. It is always Pebble."""
        emit.progress("Configuring entrypoint...")
        image_path = self.path / self.image_name

        params = ["--clear=config.entrypoint"]
        for entry in entrypoint:
            params.extend(["--config.entrypoint", entry])

        params.extend(["--clear=config.cmd"])
        _config_image(image_path, params)
        emit.progress(f"Entrypoint set to {entrypoint}")

    def set_cmd(self, command: list[str] | None = None) -> None:
        """Set the OCI image CMD.

        :param command: List of CMD arguments to set, or None to clear CMD without setting new values
        """
        emit.progress("Configuring CMD...")
        image_path = self.path / self.image_name
        cmd_params = ["--clear=config.cmd"]

        for arg in command or []:
            cmd_params.extend(["--config.cmd", arg])
        _config_image(image_path, cmd_params)
        emit.progress(f"CMD set to {command}")

    def set_default_path(self, base: str) -> None:
        """Ensure the OCI image has a sane default PATH when PATH is empty."""
        image_path = self.path / self.image_name

        env = _read_image_env_from_skopeo(image_path)
        path_value = _get_env_value(env, "PATH")

        if path_value:
            emit.debug("PATH already set on the image; not overriding.")
            return

        # Follow Pebble's lead here: if PATH is empty, use the standard one.
        # This means that containers that bypass the pebble entrypoint will
        # have the same behavior as PATH-less pebble services.
        pebble_path = Pebble.DEFAULT_ENV_PATH
        emit.debug(
            f"Setting default PATH on the image to {pebble_path!r} (base={base!r})"
        )
        _config_image(image_path, ["--config.env", f"PATH={pebble_path}"])

    def set_pebble_layer(
        self,
        services: dict[str, Any],
        checks: dict[str, Any],
        name: str,
        tag: str,
        summary: str,
        description: str,
        base_layer_dir: Path,
    ) -> None:
        """Write the provided services and checks into a Pebble layer in the filesystem.

        :param services: The Pebble services
        :param checks: The Pebble checks
        :param name: The name of the rock
        :param tag: The rock's image tag
        :param summary: The summary for the Pebble layer
        :param description: The description for the Pebble layer
        :param base_layer_dir: Path to the base layer's root filesystem
        """
        # pylint: disable=too-many-arguments
        pebble_layer_content: dict[str, Any] = {
            "summary": summary,
            "description": description,
        }

        if services:
            emit.progress(
                f"Configuring Pebble services {', '.join(list(services.keys()))}"
            )
            pebble_layer_content["services"] = services

        if checks:
            emit.progress(f"Configuring Pebble checks {', '.join(list(checks.keys()))}")
            pebble_layer_content["checks"] = checks

        pebble = Pebble()
        with tempfile.TemporaryDirectory() as tmpfs:
            tmpfs_path = Path(tmpfs)
            pebble.define_pebble_layer(
                tmpfs_path, base_layer_dir, pebble_layer_content, name
            )

            emit.progress("Writing new Pebble layer file")
            self.add_layer(tag, tmpfs_path)

    def set_environment(self, env: dict[str, str]) -> None:
        """Set the OCI image environment.

        :param env: A dictionary mapping environment variables to
            their values.
        """
        emit.progress("Configuring OCI environment...")
        image_path = self.path / self.image_name
        params: list[str] = []
        env_list: list[str] = []

        for name, value in env.items():
            env_item = f"{name}={value}"
            env_list.append(env_item)
            params.extend(["--config.env", env_item])
        _config_image(image_path, params)
        emit.progress(f"Environment set to {env_list}")

    def set_control_data(self, metadata: dict[str, Any]) -> None:
        """Create and populate the rock's control data folder.

        :param metadata: content for the rock's metadata YAML file
        """
        emit.progress("Setting the rock's control data")
        local_control_data_path = Path(tempfile.mkdtemp())

        # the rock control data structure starts with the folder ".rock"
        control_data_rock_folder = local_control_data_path / ROCK_CONTROL_DIR
        control_data_rock_folder.mkdir()

        rock_metadata_file = control_data_rock_folder / "metadata.yaml"
        with rock_metadata_file.open("w", encoding="utf-8") as rock_meta:
            yaml.dump(metadata, rock_meta)
        rock_metadata_file.chmod(0o644)

        temp_tar_file = Path(self.path, f".temp_layer.control_data.{os.getpid()}.tar")
        temp_tar_file.unlink(missing_ok=True)

        try:
            layers.archive_layer(local_control_data_path, temp_tar_file)
            _add_layer_into_image(self.path / self.image_name, temp_tar_file)
        finally:
            temp_tar_file.unlink(missing_ok=True)

        emit.progress("Control data written")
        shutil.rmtree(local_control_data_path)

    def set_annotations(self, annotations: dict[str, Any]) -> None:
        """Add the given annotations to the final image.

        :param annotations: A dictionary with each annotation/label and its value
        """
        emit.progress("Configuring labels and annotations...")
        image_path = self.path / self.image_name
        label_params = ["--clear=config.labels"]
        annotation_params = ["--clear=manifest.annotations"]

        labels_list: list[str] = []
        for label_key, label_value in annotations.items():
            label_item = f"{label_key}={label_value}"
            labels_list.append(label_item)
            label_params.extend(["--config.label", label_item])
            annotation_params.extend(["--manifest.annotation", label_item])
        # Set the labels
        _config_image(image_path, label_params)
        # Set the annotations as a copy of these labels (for OCI compliance only)
        _config_image(image_path, annotation_params)
        emit.progress(f"Labels and annotations set to {labels_list}")

    def set_media_type(self, arch: str) -> None:
        """Set the media type in the target image's manifest."""
        image_path = self.path / self.image_name
        mapping = SUPPORTED_ARCHS[arch]
        _inject_oci_fields(
            image_path,
            arch_variant=mapping.go_variant,
        )


def _copy_image(
    source: str,
    destination: str,
    *system_params: str,
    copy_params: list[str] | None = None,
) -> None:
    """Transfer images from source to destination.

    :param copy_params: Extra parameters to pass specifically to the "copy"
        skopeo command (and not to skopeo itself).
    """
    copy_extra = copy_params if copy_params else []
    _process_run(
        [
            "skopeo",
            "--insecure-policy",
            *list(system_params),
            "copy",
            *copy_extra,
            source,
            destination,
        ]
    )


def _extract_str_list(value: object) -> list[str]:
    """Return only string items if *value* is a list, otherwise []."""
    if not isinstance(value, list):
        return []
    items = cast(list[object], value)
    return [item for item in items if isinstance(item, str)]


def _read_image_env_from_skopeo(image_path: Path) -> list[str]:
    """Read image environment from `skopeo inspect` output (OCI layout)."""
    output: str = _process_run(["skopeo", "inspect", f"oci:{image_path}"]).stdout
    raw: object = json.loads(output)

    if not isinstance(raw, dict):
        return []
    data = cast(dict[str, object], raw)

    # Candidates observed across tool outputs / versions
    candidates: list[object] = [data.get("Env")]

    config = data.get("config")
    if isinstance(config, dict):
        candidates.append(cast(dict[str, object], config).get("Env"))

    for candidate in candidates:
        env = _extract_str_list(candidate)
        if env:
            return env

    return []


def _get_env_value(env: list[str], key: str) -> str | None:
    """Return the value for KEY from env entries like ['K=V', ...]. Last wins."""
    prefix = f"{key}="
    values = [e.split("=", 1)[1] for e in env if e.startswith(prefix)]
    return values[-1] if values else None


def _config_image(image_path: Path, params: list[str]) -> None:
    """Configure the OCI image."""
    _process_run(["umoci", "config", "--image", str(image_path), *params])


def _add_layer_into_image(
    image_path: Path, archived_content: Path, **kwargs: str
) -> None:
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
    _process_run([*cmd, "--history.created_by", " ".join(cmd)])


def _inject_oci_fields(image_path: Path, arch_variant: str | None = None) -> None:
    """Inject architecture variant and mediaType into existing OCI Image config.

    :param image_path: path of the OCI image
    :param arch_variant: name of the variant to inject in the OCI config
    """
    image_path_no_tag, image_tag = str(image_path).split(":", maxsplit=1)
    # pylint: disable=too-many-locals
    blobs_path = Path(image_path_no_tag) / "blobs" / "sha256"
    # Get the top level OCI index
    tl_index_path = Path(image_path_no_tag) / "index.json"
    tl_index = json.loads(tl_index_path.read_bytes())

    # The manifest of the image being built contains both the base image
    # and the target image. We need to find the manifest that matches the
    # tag of the target image, and ensure the tag is not ambiguous.
    manifest_digests: list[tuple[str, int]] = [
        (manifest["digest"].split(":")[-1], i)
        for i, manifest in enumerate(tl_index["manifests"])
        if (a := manifest.get("annotations"))
        and a.get("org.opencontainers.image.ref.name") == image_tag
    ]
    if not manifest_digests:
        raise errors.RockcraftError(
            f"Cannot find manifest for {image_tag} in {tl_index_path}"
        )
    if len(manifest_digests) > 1:
        raise errors.RockcraftError(
            f"Found multiple manifests for {image_tag} in {tl_index_path}"
        )
    manifest_digest, idx = manifest_digests[0]
    manifest_path = blobs_path / manifest_digest
    manifest_content = json.loads(manifest_path.read_bytes())

    if "mediaType" not in manifest_content:
        # Set the mediaType
        manifest_content["mediaType"] = MANIFEST_MEDIA_TYPE

    if arch_variant:
        # Get the current OCI Image Config
        image_config_digest = manifest_content["config"]["digest"].split(":")[-1]
        image_config_path = blobs_path / image_config_digest
        image_config_content = json.loads(image_config_path.read_bytes())
        # Set the variant
        image_config_content["variant"] = arch_variant

        # The OCI image config has changed, so now we need to
        # regenerate the digests
        new_image_config_bytes = json.dumps(image_config_content).encode("utf-8")
        new_image_config_digest = hashlib.sha256(new_image_config_bytes).hexdigest()
        new_image_config_path = blobs_path / new_image_config_digest
        new_image_config_path.write_bytes(new_image_config_bytes)
        image_config_path.unlink()

        manifest_content["config"]["digest"] = f"sha256:{new_image_config_digest}"
        manifest_content["config"]["size"] = len(new_image_config_bytes)

    new_manifest_bytes = json.dumps(manifest_content).encode("utf-8")
    new_manifest_digest = hashlib.sha256(new_manifest_bytes).hexdigest()
    new_manifest_path = blobs_path / new_manifest_digest
    new_manifest_path.write_bytes(new_manifest_bytes)
    manifest_path.unlink()

    tl_index["manifests"][idx]["digest"] = f"sha256:{new_manifest_digest}"
    tl_index["manifests"][idx]["size"] = len(new_manifest_bytes)
    tl_index_path.write_bytes(json.dumps(tl_index).encode("utf-8"))


def _process_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[Any]:
    """Run a command and handle its output."""
    if not Path(command[0]).is_absolute():
        command[0] = get_snap_command_path(command[0])
        emit.trace(f"Found command absolute path: {command[0]!r}")

    emit.trace(f"Execute process: {command!r}, kwargs={kwargs!r}")
    try:
        return subprocess.run(
            command,
            **kwargs,
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as err:
        msg = f"Failed to copy image: {err!s}"
        if err.stderr:
            msg += f" ({err.stderr.strip()!s})"
        raise errors.RockcraftError(msg) from err
