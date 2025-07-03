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

"""Rockcraft Lifecycle service."""

import subprocess
from pathlib import Path
from typing import cast

import distro
from craft_application import LifecycleService
from craft_parts import ProjectInfo, callbacks
from craft_parts.infos import StepInfo
from overrides import override  # type: ignore[reportUnknownVariableType]

from rockcraft import layers, utils
from rockcraft.plugins.python_common import get_python_plugins


def _use_apt_old_releases(*args, **kwargs) -> None:
    """Switch apt to use old-releases.ubuntu.com.

    For EOL releases, rather than archive.ubuntu.com and security.ubuntu.com.
    # TODO: This needs to support deb822 as well
    """
    subprocess.run(
        [
            "sed",
            "-i",
            "-e",
            "s/archive.ubuntu.com/old-releases.ubuntu.com/",
            "-e",
            "s/security.ubuntu.com/old-releases.ubuntu.com/",
            "/etc/apt/sources.list",
        ],
        check=False,
    )


def _configure_apt_overlay(path: Path, project_info: ProjectInfo) -> None:
    subprocess.run(
        [
            "sed",
            "-i",
            "-e",
            "s/archive.ubuntu.com/old-releases.ubuntu.com/",
            "-e",
            "s/security.ubuntu.com/old-releases.ubuntu.com/",
            str(path / "etc/apt/sources.list"),
        ],
        check=False,
    )


class RockcraftLifecycleService(LifecycleService):
    """Rockcraft-specific lifecycle service."""

    @override
    def setup(self) -> None:
        """Initialize the LifecycleManager with previously-set arguments."""
        # pylint: disable=import-outside-toplevel
        # This inner import is necessary to resolve a cyclic import
        from rockcraft.services import RockcraftServiceFactory

        # Configure extra args to the LifecycleManager
        project = self._services.get("project").get()

        services = cast(RockcraftServiceFactory, self._services)
        image_service = services.image
        image_info = image_service.obtain_image()

        self._manager_kwargs.update(
            base_layer_dir=image_info.base_layer_dir,
            base_layer_hash=image_info.base_digest,
            base=project.base,
            project_name=project.name,
            rootfs_dir=image_info.base_layer_dir,
        )
        super().setup()

        if utils.is_eol(distro.version()):
            callbacks.register_prologue(_use_apt_old_releases)
            callbacks.register_configure_overlay(_configure_apt_overlay)

    @override
    def post_prime(self, step_info: StepInfo) -> bool:
        """Perform base-layer pruning on primed files."""
        prime_dir = step_info.prime_dir
        base_layer_dir = step_info.rootfs_dir
        files: set[str]

        files = step_info.state.files if step_info.state else set()
        layers.prune_prime_files(prime_dir, files, base_layer_dir)

        _python_usrmerge_fix(step_info)

        return True


def _python_usrmerge_fix(step_info: StepInfo) -> None:
    """Fix 'lib64' symlinks created by the Python plugin on ubuntu@24.04 projects."""
    if step_info.project_info.base != "ubuntu@24.04":
        # The issue only affects rocks with 24.04 bases.
        return

    state = step_info.state
    if state is None:
        # Can't inspect the files without a StepState.
        return

    if state.part_properties["plugin"] not in get_python_plugins():
        # Be conservative and don't try to fix the files if they didn't come
        # from a Python plugin.
        return

    if "lib64" not in state.files:
        return

    prime_dir = step_info.prime_dir
    lib64 = prime_dir / "lib64"
    if lib64.is_symlink() and lib64.readlink() == Path("lib"):
        lib64.unlink()
