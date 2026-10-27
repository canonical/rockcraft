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
from typing import Any, cast

import craft_platforms
from craft_application import LifecycleService
from craft_cli import emit
from craft_parts.infos import StepInfo
from craft_parts.plugins import Plugin
from typing_extensions import override

from rockcraft import layers, plugins
from rockcraft.models.project import Project
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

        base_str = (
            str(project.build_base) if project.base == "bare" else str(project.base)
        )
        build_base_str = (
            str(project.build_base) if project.build_base else str(project.base)
        )
        try:
            target_release = _resolve_chisel_release(base_str)
            build_release = _resolve_chisel_release(build_base_str)
            _patch_chisel_cut_slices(target_release, build_release)
        except ValueError as exc:
            emit.debug(
                f"Could not resolve Chisel release for {base_str!r} / {build_base_str!r}: {exc}"
            )

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
        files: set[str]

        # Fix: overlay content is not included in step_info so we just list the prime_dir
        files = {str(p.relative_to(prime_dir)) for p in prime_dir.rglob("*")}

        changed = layers.prune_prime_files(prime_dir, files, base_layer_dir)
        changed |= _python_usrmerge_fix(step_info)
        changed |= _python_v2_shebang_fix(step_info)

        return changed

    @override
    @staticmethod
    def get_plugin_group(
        build_info: craft_platforms.BuildInfo,
    ) -> dict[str, type[Plugin]] | None:
        """Get the plugin group for a given base.

        Some rockcraft-specific quirks include:
        - Legacy bases (20.04, 22.04, 24.04) use Python v1, Poetry v1, and uv v1 plugins
        - Newer bases use Python v2 and omit Poetry; uv is available on 26.04
        - The dotnet v1 plugin is only available on legacy bases (20.04, 22.04, 24.04)

        :param build_info: The BuildInfo for the build, containing the build base.
        :returns: A dictionary mapping plugin names to their implementations for the given base.
        """
        return plugins.get_plugin_group(str(build_info.build_base))


def _python_usrmerge_fix(step_info: StepInfo) -> bool:
    """Fix 'lib64' symlinks created by the Python plugin on ubuntu@24.04 projects."""
    build_base = step_info.project_info.build_base
    if build_base != "ubuntu@24.04":
        # The issue only affects rocks with 24.04 build base.
        return False

    state = step_info.state
    if state is None:
        # Can't inspect the files without a StepState.
        return False

    if state.part_properties["plugin"] not in get_python_plugins(build_base):
        # Be conservative and don't try to fix the files if they didn't come
        # from a Python plugin.
        return False

    if Path("lib64") not in state.files:
        return False

    prime_dir = step_info.prime_dir
    lib64 = prime_dir / "lib64"
    if lib64.is_symlink() and lib64.readlink() == Path("lib"):
        lib64.unlink()
        return True

    return False


def _python_v2_shebang_fix(step_info: StepInfo) -> bool:
    build_base = step_info.project_info.build_base
    if build_base in ("ubuntu@20.04", "ubuntu@22.04", "ubuntu@24.04"):
        # The issue only affects rocks with 25.10 and newer build bases.
        return False

    state = step_info.state
    if state is None:
        # Can't inspect the files without a StepState.
        return False

    if state.part_properties["plugin"] not in get_python_plugins(build_base):
        # Be conservative and don't try to fix the files if they didn't come
        # from a Python plugin.
        return False

    prime_dir = step_info.prime_dir

    # The Python interpreter can come from either the part's install dir, or from the
    # stage.
    install_dir = step_info.part_install_dir
    install_re = re.compile(f"#!{install_dir}/.*/python3.*$")
    stage_dir = step_info.stage_dir
    stage_re = re.compile(f"#!{stage_dir}/.*/python3.*$")

    regex_and_dirs = [(install_re, install_dir), (stage_re, stage_dir)]
    changed = False

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
            changed = True

    return changed


def _resolve_chisel_release(base_str: str) -> str:
    """Resolve a base or build-base string into a Chisel release name (e.g. 'ubuntu-26.10')."""
    if "@" not in base_str and base_str != "devel":
        base_str = f"ubuntu@{base_str}"
    distro = craft_platforms.DistroBase.from_str(base_str)
    series = distro.series
    if series == "devel":
        for info in Project._get_devel_bases():  # noqa: SLF001 (private member access)
            if info.devel_base.value == "devel":
                series = info.current_devel_base.value
                break
    return f"{distro.distribution}-{series}"


def _patch_chisel_cut_slices(target_release: str, build_release: str) -> None:
    """Patch craft_parts chisel.cut_slices to explicitly specify the release."""
    import logging
    import subprocess
    from io import StringIO

    from craft_parts.packages import chisel
    from craft_parts.packages import errors as craft_errors
    from craft_parts.packages.base import logger as chisel_logger
    from craft_parts.utils import os_utils

    def _cut_slices_with_release(
        slices: list[str], target_dir: Path, *args: Any, **kwargs: Any
    ) -> None:
        """Cut Chisel slices into a destination path with explicit release."""
        release = (
            build_release
            if "build_slices" in Path(target_dir).parts
            else target_release
        )
        output_stream = StringIO()
        handler = logging.StreamHandler(stream=output_stream)
        chisel_logger.addHandler(handler)
        try:
            os_utils.process_run(
                [
                    "chisel",
                    "cut",
                    f"--release={release}",
                    "--ignore=unmaintained",
                    "--ignore=unstable",
                    f"--root={target_dir}",
                    *slices,
                ],
                chisel_logger.debug,
                *args,
                **kwargs,
            )
        except subprocess.CalledProcessError as err:
            command_output = output_stream.getvalue()
            raise craft_errors.ChiselError(
                slices=slices, output=command_output
            ) from err
        finally:
            chisel_logger.removeHandler(handler)
            handler.close()

    chisel.cut_slices = _cut_slices_with_release
