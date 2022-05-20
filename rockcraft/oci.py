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

from datetime import datetime
from email.mime import base
import logging
import os
import random
from re import U
import shutil
import subprocess
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from craft_cli import CraftError, emit
from pydantic import conlist

from rockcraft.project import UserAccount, UserInfo
from rockcraft.errors import ConfigurationError
from . import utils


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Image:
    """A local OCI image.

    :param image_name: The name of this image in ``name:tag`` format.
    :param path: The path to this image in the local filesystem.
    """

    image_name: str
    path: Path
    # Allowed UID range in Rockcraft: 589824 - 655359 (0x90000-0x9ffff)
    # (similar to snapd, which has (0x80000-0x8ffff))
    allowed_uid_range: conlist(int) = range(589824, 655359 + 1)

    @staticmethod
    def _sanitize_new_user(existing_users: List[str], existing_uids: List[int], username: str, uid: int = None, uid_range: List[int] = None) -> Tuple[str, str]:
        """Makes sure the new user account doesn't exist yet, and generated a UID if necessary

        :param existing_users: List with all the users which already exist in the base image
        :type existing_users: List[str]
        :param existing_uids: List with all the user IDs which already exist in the base image
        :type existing_uids: List[int]
        :param username: name of the user account to be sanitized
        :type username: str
        :param uid: corresponding user ID, defaults to None
        :type uid: int, optional
        :param uid_range: allowed range of IDs to be used if there's a need to generate a new UID, defaults to None
        :type uid_range: List[int], optional
        :raises ConfigurationError: when either the username or UID already exist in the base image
        :return: the sanitized username and corresponding user ID
        :rtype: Tuple[str, str]
        """
        user_id = uid if uid else random.choice(list(set(uid_range) - set(existing_uids)))
        if username in existing_users or uid in existing_uids:
            raise ConfigurationError(f"The provided {username}:{uid} is already configured in the base image")

        return username, user_id

    @staticmethod
    def _sanitize_new_group(existing_groups: List[str], existing_gids: List[int], group: str = None, gid: int = None, gid_range: List[int] = None) -> Tuple[str, str]:
        """Sets the new user's group, making sure it doesn't conflict with existing groups, and creating it if needed

        :param existing_groups: List with all the groups which already exist in the base image
        :type existing_groups: List[str]
        :param existing_gids: List with all the group IDs which already exist in the base image
        :type existing_gids: List[int]
        :param group: name of the group to sanitize, defaults to None
        :type group: str, optional
        :param gid: corresponding group ID, which takes precedence over "group" when cross-checking for existing matches, defaults to None
        :type gid: int, optional
        :param gid_range: allowed range of IDs to be used if there's a need to generate a new GID, defaults to None
        :type gid_range: List[int], optional
        :raises ConfigurationError: if the provided group name is different from the one the GID already belongs to
        :return: the sanitized group and corresponding group ID
        :rtype: Tuple[str, str]
        """
        if gid and gid in existing_gids:
            group_from_gid = existing_groups[existing_gids.index(gid)]
            if group and group != group_from_gid:
                raise ConfigurationError(
                    f'The pair {group}:{gid} does not match with '
                    f'the existing group {group_from_gid} with the GID {gid}')
            group = group_from_gid
        elif group and group in existing_groups:
            gid = existing_gids[existing_groups.index(group)]

        if not gid:
            gid = random.choice(list(set(gid_range) - set(existing_gids)))

        if not group:
            # group:gid not provided - random group name
            group = f"unnamedgroup{gid}"

        return group, gid

    @staticmethod
    def _sanitize_new_user_info(user_info: UserInfo) -> Tuple[str, str, str, str, str]:
        """Extracts the new user's information

        :param user_info: object of UserInfo, containing the optional user information
        :type user_info: UserInfo
        :return: the user's full name, room number, work phone, home phone, and other info
        :rtype: Tuple[str, str, str, str, str]
        """
        full_name = str(getattr(user_info, "full_name", "") or "")
        room_number = str(getattr(user_info, "room_number", "") or "")
        work_phone = str(getattr(user_info, "work_phone", "") or "")
        home_phone = str(getattr(user_info, "home_phone", "") or "")
        other = str(getattr(user_info, "other", "") or "")

        return full_name, room_number, work_phone, home_phone, other

    def _sanitize_new_user_home(self, home: Path, base_rootfs: Path) -> str:
        """Configures the new user's home directory, creating it if it doesn't exist

        :param home: user's home directory
        :type home: Path
        :param base_rootfs: location of the base image filesystem, to check if "home" already exists
        :type base_rootfs: Path
        :return: the sanitized home directory
        :rtype: str
        """
        home = home if home else Path("/nonexistent")

        home_in_base_rootfs = base_rootfs / str(home).lstrip('/')
        if not os.path.exists(home_in_base_rootfs):
            os.mkdir(home_in_base_rootfs)
            _insert_into_image(self.path / self.image_name, home_in_base_rootfs, home)

        return str(home)
    
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
        
    def set_default_user(self, user: str) -> None:
        """Set the default runtime user for the OCI image.

        :param user: name of the default user (must already exist)
        :type user: str
        """
        emit.progress("Configuring default user...")
        image_path = self.path / self.image_name
        params = ["--config.user", user]
        _config_image(image_path, params)
        emit.message(f"Default user set to {user}", intermediate=True)
        
    def create_users(self, user_accounts: List[UserAccount], base_rootfs_path: Path) -> List[Path]:
        """Scans the base image filesystems and manually creates new users and groups

        :param user_accounts: list of user accounts to be created
        :type user_accounts: List[UserAccount]
        :param base_rootfs_path: Path to the base filesystem
        :type base_rootfs_path: Path

        :returns: the list of files that were changed in the base image 
        :rtype: List[Path]
        """
        existing_passwd_file = base_rootfs_path / "etc/passwd"
        existing_group_file = base_rootfs_path / "etc/group"
        existing_shadow_file = base_rootfs_path / "etc/shadow"

        existing_users, existing_uids = utils.extract_values_from_file(
            existing_passwd_file,
            ':',
            {0: 'str', 2: 'int'},
            always_return=True
        )

        existing_groups, existing_gids = utils.extract_values_from_file(
            existing_group_file,
            ':',
            {0: 'str', 2: 'int'},
            always_return=True
        )

        passwd_content, shadow_content, group_content = ([] for i in range(3))
        for account in user_accounts:
            username, *uid = account.username.split(':')
            ## USERNAME + UID
            username, uid = self._sanitize_new_user(existing_users,
                                                    existing_uids,
                                                    username,
                                                    uid=int(uid[0]) if uid else None,
                                                    uid_range=self.allowed_uid_range)

            existing_uids.append(uid)
            existing_users.append(username)

            # GROUP + GID
            group, *gid = str(getattr(account, 'group', "") or "").split(':')
            group, gid = self._sanitize_new_group(existing_groups,
                                                  existing_gids,
                                                  group=group if group else username,
                                                  gid=int(gid[0]) if gid else None,
                                                  gid_range=self.allowed_uid_range)

            group_content.append(f"{group}:x:{gid}:")
            existing_gids.append(gid)
            existing_groups.append(group)

            # USER INFO
            user_info = self._sanitize_new_user_info(account.user_info)

            # USER HOME
            home = self._sanitize_new_user_home(account.home, base_rootfs_path)

            # USER COMMAND
            command = account.command if account.command else "/usr/sbin/nologin"

            passwd_new_line = f"{username}:x:{uid}:{gid}:{user_info[0]},{user_info[1]},{user_info[2]},{user_info[3]},{user_info[4]}:{home}:{command}"
            passwd_content.append(passwd_new_line)

        with open(existing_passwd_file, 'a+') as passwdf:
            passwdf.write('\n'.join(map(str, passwd_content)) + '\n')

        with open(existing_group_file, 'a+') as groupf:
            groupf.write('\n'.join(map(str, group_content)) + '\n')

        changed_files = [existing_passwd_file, existing_group_file]
        if os.path.exists(existing_shadow_file):
            # TODO: TBD - no password accepted at the moment
            days_since_epoch = (datetime.utcnow() - datetime(1970, 1, 1)).days
            shadow_content.append(f"{username}:*:{days_since_epoch}:0:99999:7:::")
            # only add the shadow file is there's already one in the base image
            with open(existing_shadow_file, 'a+') as shadowf:
                shadowf.write('\n'.join(map(str, shadow_content)) + '\n')

            changed_files.append(existing_shadow_file)

        return changed_files

    def insert_content(self, source: Path, target: Path) -> None:
        """Inserts content into the OCI image

        :param source: source to be inserted
        :type source: Path
        :param target: Path in the OCI image where to insert the source content
        :type target: Path
        """
        image_path = self.path / self.image_name
        _insert_into_image(image_path, source, target)


def _insert_into_image(image_path: Path, source: Path, target: Path) -> None:
    """Inserts content into the OCI image

        :param image_path: where to find the OCI image
        :type image_path: Path
        :param source: source to be inserted
        :type source: Path
        :param target: Path in the OCI image where to insert the source content
        :type target: Path
        """
    _process_run(["umoci", "insert", "--image", str(image_path), str(source), str(target)])


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
