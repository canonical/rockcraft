# Copyright 2020-2021 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For further info, check https://github.com/canonical/charmcraft

"""Utilities for rockcraft."""

import distutils.util
import logging
import os
import pathlib
import sys
from collections import namedtuple
from typing import Optional

logger = logging.getLogger(__name__)

OSPlatform = namedtuple("OSPlatform", "system release machine")


def is_managed_mode():
    """Check if rockcraft is running in a managed environment."""
    managed_flag = os.getenv("ROCKCRAFT_MANAGED_MODE", "n")
    return distutils.util.strtobool(managed_flag) == 1


def get_managed_environment_home_path():
    """Path for home when running in managed environment."""
    return pathlib.Path("/root")


def get_managed_environment_project_path():
    """Path for project when running in managed environment."""
    return get_managed_environment_home_path() / "project"


def get_managed_environment_snap_channel() -> Optional[str]:
    """User-specified channel to use when installing Rockcraft snap from Snap Store.

    :returns: Channel string if specified, else None.
    """
    return os.getenv("ROCKCRAFT_INSTALL_SNAP_CHANNEL")


def confirm_with_user(prompt, default=False) -> bool:
    """Query user for yes/no answer.

    If stdin is not a tty, the default value is returned.

    If user returns an empty answer, the default value is returned.
    returns default value.

    :returns: True if answer starts with [yY], False if answer starts with [nN],
        otherwise the default.
    """
    if is_managed_mode():
        raise RuntimeError("confirmation not yet supported in managed-mode")

    if not sys.stdin.isatty():
        return default

    choices = " [Y/n]: " if default else " [y/N]: "

    reply = str(input(prompt + choices)).lower().strip()
    if reply and reply[0] == "y":
        return True

    if reply and reply[0] == "n":
        return False

    return default
