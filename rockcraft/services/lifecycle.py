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

import re
from pathlib import Path
from typing import cast

from craft_application import LifecycleService
from craft_parts.infos import StepInfo
from overrides import override  # type: ignore[reportUnknownVariableType]

from rockcraft import layers
from rockcraft.plugins.python_common import get_python_plugins


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

        base = project.effective_base
        usrmerged_by_default = True

        # Bases older than 25.10 do not get usermerged install dirs by default
        if base in ("ubuntu@20.04", "ubuntu@22.04", "ubuntu@24.04"):
            usrmerged_by_default = False

        self._manager_kwargs.update(
            base_layer_dir=image_info.base_layer_dir,
            base_layer_hash=image_info.base_digest,
            base=project.base,
            build_base=project.build_base,
            project_name=project.name,
            rootfs_dir=image_info.base_layer_dir,
            usrmerged_by_default=usrmerged_by_default,
        )
        super().setup()

    @override
    def post_prime(self, step_info: StepInfo) -> bool:
        """Perform base-layer pruning on primed files."""
        prime_dir = step_info.prime_dir
        base_layer_dir = step_info.rootfs_dir
        files: set[Path]

        files = step_info.state.files if step_info.state else set()
        layers.prune_prime_files(prime_dir, files, base_layer_dir)

        _python_usrmerge_fix(step_info)
        _python_v2_shebang_fix(step_info)

        return True


def _python_usrmerge_fix(step_info: StepInfo) -> None:
    """Fix 'lib64' symlinks created by the Python plugin on ubuntu@24.04 projects."""
    build_base = step_info.project_info.build_base
    if build_base != "ubuntu@24.04":
        # The issue only affects rocks with 24.04 build base.
        return

    state = step_info.state
    if state is None:
        # Can't inspect the files without a StepState.
        return

    if state.part_properties["plugin"] not in get_python_plugins(build_base):
        # Be conservative and don't try to fix the files if they didn't come
        # from a Python plugin.
        return

    if Path("lib64") not in state.files:
        return

    prime_dir = step_info.prime_dir
    lib64 = prime_dir / "lib64"
    if lib64.is_symlink() and lib64.readlink() == Path("lib"):
        lib64.unlink()


def _python_v2_shebang_fix(step_info: StepInfo) -> None:
    build_base = step_info.project_info.build_base
    if build_base in ("ubuntu@20.04", "ubuntu@22.04", "ubuntu@24.04"):
        # The issue only affects rocks with 25.10 and newer build bases.
        return

    state = step_info.state
    if state is None:
        # Can't inspect the files without a StepState.
        return

    if state.part_properties["plugin"] not in get_python_plugins(build_base):
        # Be conservative and don't try to fix the files if they didn't come
        # from a Python plugin.
        return

    prime_dir = step_info.prime_dir

    # The Python interpreter can come from either the part's install dir, or from the
    # stage.
    install_dir = step_info.part_install_dir
    install_re = re.compile(f"#!{install_dir}/.*/python3.*$")
    stage_dir = step_info.stage_dir
    stage_re = re.compile(f"#!{stage_dir}/.*/python3.*$")

    regex_and_dirs = [(install_re, install_dir), (stage_re, stage_dir)]

    for filename in state.files:
        filepath = prime_dir / filename
        if not filepath.is_file():
            # File might have been pruned out
            continue
        newline = ""
        remainder = ""
        replaced = False
        with filepath.open("r") as f:
            # Read the first line and check whether it matches the install or stage dirs.
            try:
                line = f.readline()
            except UnicodeDecodeError:
                # File is not text; ignore it
                continue
            for base_re, base_dir in regex_and_dirs:
                if base_re.match(line):
                    newline = line.replace(str(base_dir), "")
                    remainder = f.read()
                    replaced = True
                    break
        if replaced:
            filepath.write_text(newline + remainder)
