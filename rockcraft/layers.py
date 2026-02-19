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

"""Handling of files and directories for rocks image layers."""

import os
import tarfile
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

from craft_cli import emit
from craft_parts.executor.collisions import paths_collide
from craft_parts.overlays import overlays
from craft_parts.permissions import Permissions
from craft_parts.utils import process

from rockcraft import errors


def archive_layer(
    new_layer_dir: Path,
    temp_tar_file: Path,
    base_layer_dir: Path | None = None,
) -> None:
    """Prepare new OCI layer by archiving its content into tar file.

    :param new_layer_dir: path to the content to be archived into a layer.
    :param temp_tar_file: path to the temporary tar file holding the archived content.
    :param base_layer_dir: optional path to the filesystem containing the extracted
        base below this new layer. Used to preserve lower-level directory symlinks,
        like the ones from Debian/Ubuntu's usrmerge.
    """
    candidates = _gather_layer_paths(new_layer_dir, base_layer_dir)
    layer_paths = _merge_layer_paths(candidates)

    layer_contents: list[Path] = []
    transforms: list[str] = []
    with TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        # Just create an empty tar file if there's nothing to put in the layer
        # GNU tar simply refuses to create an actual empty tar file though, so just use
        # python's tarfile
        if not layer_paths:
            with tarfile.open(temp_tar_file, "w"):
                pass
            return

        # # Walk in reverse to avoid encountering not-yet created dirs
        # for arcname in sorted(layer_paths, reverse=True):
        #     filepath = layer_paths[arcname]
        #     emit.debug(f"Adding to layer: {filepath} as {arcname!r}")

        #     # Construct a new file at `arcname` with the same contents as `filepath`.
        #     # This emulates the `arcname` parameter of `tarfile.open()`, which is not
        #     # present in GNU tar.
        #     new_path = tmppath / arcname
        #     layer_contents.append(new_path.relative_to(tmppath))
        #     if new_path.is_dir() and new_path.exists():
        #         continue
        #     new_path.parent.mkdir(parents=True, exist_ok=True)
        #     filepath.rename(new_path)

        for arcname, oldname in layer_paths.items():
            oldname = str(oldname).removeprefix("/")
            transforms.extend(["--transform", f"s|{str(oldname)}|{arcname}|"])

        # GNU tar is being used instead of Python's `tarfile` as it does not support
        # special file attributes like xattrs.
        tar_command: list[str | Path] = [
            "tar",
            "-cf",
            temp_tar_file.resolve(),
            # Don't descend automatically into directories
            "--no-recursion",
            # Preserve all those fancy attributes
            "--acls",
            "--xattrs",
            "--selinux",
            *transforms,
            # Tarball sorted files, so that the directories are always listed before
            # any files that they contain (otherwise tools like Docker might choke on
            # the layer tarball).
            *sorted(str(p) for p in layer_paths.values()),
        ]
        process.run(tar_command, cwd=tmppath, check=True)


def prune_prime_files(prime_dir: Path, files: set[str], base_layer_dir: Path) -> None:
    """Remove (prune) files in a prime directory if they exist in the base layer.

    Given a set of filenames ``files``, this function will remove (prune) all those
    filenames from prime dir ``prime_dir`` if the corresponding sub path exists in
    the extracted base layer directory ``base_layer_dir`` with same contents and
    permissions.

    For example, "{prime_dir}/dir/subdir/file1" will be pruned if the matching file
    "{base_layer_dir}/dir/subdir/file1" exists and has the same contents, owner,
    group, and permission bits.

    :param prime_dir: The directory containing the lifecycle's primed contents.
    :param files: The set of filenames added to ``prime_dir``, as provided by
        the corresponding post_step lifecycle callback.
    :param base_layer_dir: The directory where the base layer was extracted.
    """
    emit.debug("Pruning primed files that already exist on base layer...")
    for filename in files:
        base_layer_file = base_layer_dir / filename
        if base_layer_file.is_file():
            prime_file = prime_dir / filename
            if _all_compatible_files([base_layer_file, prime_file]):
                emit.debug(f"Pruning: {prime_file} as it exists on the base")
                prime_file.unlink()
            else:
                emit.debug(
                    f"{prime_file} exists on the base but with different contents or permissions"
                )


def _gather_layer_paths(
    new_layer_dir: Path, base_layer_dir: Path | None = None
) -> dict[str, list[Path]]:
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
    result: defaultdict[str, list[Path]] = defaultdict(list)
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


def _merge_layer_paths(candidate_paths: dict[str, list[Path]]) -> dict[str, Path]:
    """Merge ``candidate_paths`` into a single path per name.

    This function handles the case where multiple paths refer to the same name
    in the new layer; if all paths are directories with the same ownership and
    permissions then a single one is used (they are all equivalent). All other
    cases (directories with different attributes, files) will raise an error.

    :return:
        A dict where the values are Paths and the keys are the names those paths
        correspond to in the new layer.
    """
    result: dict[str, Path] = {}

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
    relative_path: Path, base_layer_dir: Path | None
) -> Path | None:
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
        return lower_path.readlink()

    return None


def _all_compatible_directories(paths: list[Path]) -> bool:
    """Whether ``paths`` contains only directories with the same ownership and permissions."""
    if not all(p.is_dir() for p in paths):
        return False

    if len(paths) < 2:  # noqa: PLR2004
        return True

    def stat_props(stat: os.stat_result) -> tuple[int, int, int]:
        return stat.st_uid, stat.st_gid, stat.st_mode

    first_stat = stat_props(paths[0].stat())

    for other_path in paths[1:]:
        other_stat = stat_props(other_path.stat())
        if first_stat != other_stat:
            emit.debug(
                f"Path attributes differ for '{paths[0]}' and '{other_path}': "
                f"{first_stat} vs {other_stat}"
            )
            return False

    return True


def _all_compatible_files(paths: list[Path]) -> bool:
    """Whether ``paths`` contains only files with the same attributes and contents."""
    if not all(p.is_file() for p in paths):
        return False

    if len(paths) < 2:  # noqa: PLR2004
        return True

    first_file = paths[0]

    permissions_first = [_get_permissions(first_file)]

    for other_file in paths[1:]:
        permissions_other = [_get_permissions(other_file)]
        if paths_collide(
            str(first_file), str(other_file), permissions_first, permissions_other
        ):
            return False

    return True


def _get_permissions(filename: Path) -> Permissions:
    """Create a Permissions object for a given Path."""
    stat = filename.stat()
    return Permissions(owner=stat.st_uid, group=stat.st_gid, mode=oct(stat.st_mode))
