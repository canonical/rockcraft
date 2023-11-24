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

"""Handling of files and directories for ROCKs image layers."""
import os
import tarfile
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Tuple

from craft_cli import emit
from craft_parts.executor.collisions import paths_collide
from craft_parts.overlays import overlays

from rockcraft import errors


def archive_layer(
    new_layer_dir: Path,
    temp_tar_file: Path,
    base_layer_dir: Optional[Path] = None,
) -> None:
    """Prepare new OCI layer by archiving its content into tar file.

    :param new_layer_dir: path to the content to be archived into a layer
    :param temp_tar_file: path to the temporary tar file holding the archived content
    :param base_layer_dir: optional path to the filesystem containing the extracted
        base below this new layer. Used to preserve lower-level directory symlinks,
        like the ones from Debian/Ubuntu's usrmerge.
    """
    candidates = _gather_layer_paths(new_layer_dir, base_layer_dir)
    layer_paths = _merge_layer_paths(candidates)

    with tarfile.open(temp_tar_file, mode="w") as tar_file:
        # Iterate on sorted keys, so that the directories are always listed before
        # any files that they contain (otherwise tools like Docker might choke on
        # the layer tarball).
        for arcname in sorted(layer_paths):
            filepath = layer_paths[arcname]
            emit.debug(f"Adding to layer: {filepath} as '{arcname}'")
            tar_file.add(filepath, arcname=arcname, recursive=False)


def _gather_layer_paths(
    new_layer_dir: Path, base_layer_dir: Optional[Path] = None
) -> Dict[str, List[Path]]:
    """Map paths in ``new_layer_dir`` to names in a layer file.

    See ``_archive_layer()`` for the parameters.

    :return:
      A dict where the value is a path (file or dir) in ``new_layer_dir`` and the
      key is the name that this path should have in the tarball for the layer.
    """
    # pylint: disable=too-many-locals

    class LayerLinker:
        """Helper to keep track of paths between the upper and lower layer."""

        upper_prefix: str = ""
        lower_prefix: str = ""

        def reset(self, upper_prefix: str, lower_prefix: str) -> None:
            """Set a correspondence between a path in the upper layer and a path the lower layer.

            For example, if in the lower layer `bin` is a symlink to `usr/bin`,
            calling ``reset("bin", "usr/bin")`` will let this LayerLinker convert
            upper layer paths in "bin" to "usr/bin" when calling ``get_target_path()``.
            """
            self.upper_prefix = upper_prefix
            self.lower_prefix = lower_prefix

        def get_target_path(self, path: Path) -> Path:
            """Get the path that should be used when adding ``path`` to the archive.

            :return:
                If ``path`` starts with ``upper_prefix``, the returned Path is ``path``
                with that prefix replaced with ``lower_prefix``. Otherwise, the return
                is ``path`` unchanged.
            """
            if not self.upper_prefix:
                return path

            str_path = str(path)
            if str_path.startswith(self.upper_prefix):
                return Path(str_path.replace(self.upper_prefix, self.lower_prefix, 1))
            return path

    layer_linker = LayerLinker()
    result: DefaultDict[str, List[Path]] = defaultdict(list)
    for dirpath, subdirs, filenames in os.walk(new_layer_dir):
        # Sort `subdirs` in-place, to ensure that `os.walk()` iterates on
        # them in sorted order.
        subdirs.sort()

        upper_subpath = Path(dirpath)

        # The path with `new_layer_dir` as the "root"
        relative_path = upper_subpath.relative_to(new_layer_dir)

        # Handle adding an entry for the directory. We skip this IF:
        # - The directory is the root (to skip a spurious "." entry), OR
        # - The directory is NOT an opaque OCI entry AND
        # - The directory's exists on ``base_layer_dir`` as a symlink to another
        #   directory (like in usrmerge).
        if upper_subpath != new_layer_dir:
            upper_is_not_opaque_dir = not overlays.is_oci_opaque_dir(upper_subpath)
            lower_symlink_target = _symlink_target_in_base_layer(
                relative_path, base_layer_dir
            )
            lower_is_symlink = lower_symlink_target is not None

            if upper_is_not_opaque_dir and lower_is_symlink:
                emit.debug(
                    f"Skipping {upper_subpath} because it exists as a symlink on the lower layer"
                )
                layer_linker.reset(str(relative_path), str(lower_symlink_target))
            else:
                lower_path = layer_linker.get_target_path(relative_path)
                result[f"{lower_path}"].append(upper_subpath)

        # Add each file in the directory.
        for name in filenames:
            archive_path = layer_linker.get_target_path(relative_path / name)
            result[f"{archive_path}"].append(upper_subpath / name)

        # Add each subdir in the directory if it's a symlink, because the os.walk()
        # call will not enter them.
        for subdir in subdirs:
            upper_subdir_path = upper_subpath / subdir
            if upper_subdir_path.is_symlink():
                archive_path = layer_linker.get_target_path(relative_path / subdir)
                result[f"{archive_path}"].append(upper_subdir_path)

    return result


def _merge_layer_paths(candidate_paths: Dict[str, List[Path]]) -> Dict[str, Path]:
    """Merge ``candidate_paths`` into a single path per name.

    This function handles the case where multiple paths refer to the same name
    in the new layer; if all paths are directories with the same ownership and
    permissions then a single one is used (they are all equivalent). All other
    cases (directories with different attributes, files) will raise an error.

    :return:
        A dict where the values are Paths and the keys are the names those paths
        correspond to in the new layer.
    """
    result: Dict[str, Path] = {}

    for name, paths in candidate_paths.items():
        if len(paths) == 1:
            result[name] = paths[0]
            continue

        if _all_compatible_directories(paths):
            emit.debug(
                f"Multiple directories pointing to '{name}': {', '.join(map(str, paths))}"
            )
            result[name] = paths[0]
            continue

        if _all_compatible_files(paths):
            emit.debug(
                f"Multiple files pointing to '{name}': {', '.join(map(str, paths))}"
            )
            result[name] = paths[0]
            continue

        # We currently don't try to do any kind of path conflict resolution; if
        # the paths aren't all directories with the same ownership and permissions,
        # bail out with an error.
        raise errors.LayerArchivingError(
            f"Conflicting paths pointing to '{name}': {', '.join(map(str, paths))}"
        )

    return result


def _symlink_target_in_base_layer(
    relative_path: Path, base_layer_dir: Optional[Path]
) -> Optional[Path]:
    """If `relative_path` is a dir symlink in `base_layer_dir`, return its 'target'.

    This function checks if `relative_path` exists in the base `base_layer_dir` as
    a symbolic link to another directory; if it does, the function will return the
    symlink target. In all other cases, the function returns None.

    :param relative_path: The subpath to check.
    :param base_layer_dir: The directory with the contents of the base layer.
    """
    if base_layer_dir is None:
        return None

    lower_path = base_layer_dir / relative_path

    if lower_path.is_symlink():
        return Path(os.readlink(lower_path))

    return None


def _all_compatible_directories(paths: List[Path]) -> bool:
    """Whether ``paths`` contains only directories with the same ownership and permissions."""
    if not all(p.is_dir() for p in paths):
        return False

    if len(paths) < 2:
        return True

    def stat_props(stat: os.stat_result) -> Tuple[int, int, int]:
        return stat.st_uid, stat.st_gid, stat.st_mode

    first_stat = stat_props(paths[0].stat())

    for other_path in paths[1:]:
        other_stat = stat_props(other_path.stat())
        if first_stat != other_stat:
            emit.debug(
                (
                    f"Path attributes differ for '{paths[0]}' and '{other_path}': "
                    f"{first_stat} vs {other_stat}"
                )
            )
            return False

    return True


def _all_compatible_files(paths: List[Path]) -> bool:
    """Whether ``paths`` contains only files with the same attributes and contents."""
    if not all(p.is_file() for p in paths):
        return False

    if len(paths) < 2:
        return True

    first_file = paths[0]

    for other_file in paths[1:]:
        if paths_collide(str(first_file), str(other_file)):
            return False

    return True
