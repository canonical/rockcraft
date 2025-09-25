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

"""Rockcraft-specific plugins."""

from .register import get_plugins, register
from craft_providers.lxd import LXDInstance
import os

__all__ = ["get_plugins", "register"]


def launch(
    self: object,
    *,
    image: str,
    image_remote: str,
    map_user_uid: bool = False,
    ephemeral: bool = False,
    uid: int | None = None,
) -> None:
    """Launch instance.

    :param image: Image name to launch.
    :param image_remote: Image remote name.
    :param map_user_uid: Whether id mapping should be used.
    :param uid: If ``map_user_uid`` is True,
                the host user ID to map to instance root.
    :param ephemeral: Flag to enable ephemeral instance.

    :raises LXDError: On unexpected error.
    """
    config_keys = {}

    if map_user_uid:
        if not uid:
            uid = os.getuid()
        config_keys["raw.idmap"] = f"both {uid!s} 0"

    # if self._intercept_mknod:
    #     if not self._host_supports_mknod():
    #         warnings.warn(
    #             "Application configured to intercept guest mknod calls, "
    #             "but the host OS does not support intercepting mknod."
    #         )
    #     else:
    #         config_keys["security.syscalls.intercept.mknod"] = "true"

    config_keys["security.nesting"] = "true"

    self.lxc.launch(
        config_keys=config_keys,
        ephemeral=ephemeral,
        instance_name=self.instance_name,
        image=image,
        image_remote=image_remote,
        project=self.project,
        remote=self.remote,
    )


LXDInstance.launch = launch
