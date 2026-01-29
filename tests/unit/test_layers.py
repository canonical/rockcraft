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
import os
import re
import stat
import sys
import tarfile
from pathlib import Path

import pytest
from craft_parts.overlays import overlays
from rockcraft import errors, layers


def get_tar_contents(tar_path: Path) -> list[str]:
    with tarfile.open(tar_path, "r") as tar_file:
        return tar_file.getnames()


def duplicate_dirs_setup(tmp_path) -> tuple[Path, Path]:
    """Create a filetree with an upper layer and a fake 'rootfs' structure.

    layer_dir/
      |- bin/dir1/a.txt
      |- usr/bin/dir1/b.txt
    rootfs/
      |- usr/bin/
      |- bin ----> usr/bin (symlink)

    returns a tuple with (layer_dir, rootfs).
    """

    layer_dir = tmp_path / "layer_dir"
    layer_dir.mkdir()

    # The new layer has "bin/dir1/a.txt" and "usr/bin/dir1/b.txt".
    (layer_dir / "bin/dir1").mkdir(parents=True)
    (layer_dir / "bin/dir1/a.txt").touch()
    (layer_dir / "usr/bin/dir1").mkdir(parents=True)
    (layer_dir / "usr/bin/dir1/b.txt").touch()

    rootfs_dir = tmp_path / "rootfs"
    rootfs_dir.mkdir()
    # In the base layer "bin" is a symlink to "usr/bin"
    (rootfs_dir / "usr/bin").mkdir(parents=True)
    (rootfs_dir / "bin").symlink_to("usr/bin")

    return layer_dir, rootfs_dir


def test_archive_layer_directories(tmp_path):
    """Test that adding a directory as a layer explicitly preserves subdirs"""
    layer_dir = tmp_path / "layer_dir"
    layer_dir.mkdir()

    (layer_dir / "first").mkdir()
    (layer_dir / "first/first.txt").touch()

    (layer_dir / "second").mkdir()
    (layer_dir / "second/second.txt").touch()

    temp_tar_path = tmp_path / "layer.tar"
    layers.archive_layer(layer_dir, temp_tar_path)
    temp_tar_contents = get_tar_contents(temp_tar_path)

    expected_tar_contents = [
        "first",
        "first/first.txt",
        "second",
        "second/second.txt",
    ]
    assert temp_tar_contents == expected_tar_contents


def test_archive_layer_symlinks(tmp_path):
    """
    Test creating a new layer with symlinks (both file and dir).
    """
    layer_dir = tmp_path / "layer_dir"
    layer_dir.mkdir()

    (layer_dir / "first_dir").mkdir()
    (layer_dir / "first_file").touch()

    (layer_dir / "second_dir").symlink_to("first_dir", target_is_directory=True)
    (layer_dir / "second_file").symlink_to("first_file", target_is_directory=False)

    temp_tar_path = tmp_path / "layer.tar"
    layers.archive_layer(layer_dir, temp_tar_path)
    temp_tar_contents = get_tar_contents(temp_tar_path)

    expected_tar_contents = [
        "first_dir",
        "first_file",
        "second_dir",
        "second_file",
    ]
    assert temp_tar_contents == expected_tar_contents


def test_archive_layer_with_base_layer_dir(tmp_path):
    """Test creating a layer with a base layer dir for reference."""
    layer_dir = tmp_path / "layer_dir"
    layer_dir.mkdir()

    (layer_dir / "first").mkdir()
    (layer_dir / "first/first.txt").touch()

    (layer_dir / "second").mkdir()
    (layer_dir / "second/second.txt").touch()

    # Create a dir tree to act as extracted "base"
    # It contains a "first" dir and a "second" symlink pointing to "first"
    rootfs_dir = tmp_path / "rootfs"
    rootfs_dir.mkdir()

    (rootfs_dir / "first").mkdir()
    (rootfs_dir / "second").symlink_to("first")

    temp_tar_path = tmp_path / "layer.tar"
    layers.archive_layer(layer_dir, temp_tar_path, base_layer_dir=rootfs_dir)
    temp_tar_contents = get_tar_contents(temp_tar_path)

    # The tarfile must *not* contain the "./second" dir entry, to preserve
    # the base layer symlink. Additionally, the file "second.txt" must
    # be listed as inside "first/", and not "second/".
    expected_tar_contents = [
        "first",
        "first/first.txt",
        "first/second.txt",
    ]
    assert temp_tar_contents == expected_tar_contents


def test_archive_layer_with_base_layer_dir_opaque(tmp_path):
    """
    Test creating a layer with a base layer dir for reference, but the new
    layer hides one of the dirs in the base layer via an opaque whiteout file.
    """
    layer_dir = tmp_path / "layer_dir"
    layer_dir.mkdir()

    (layer_dir / "first").mkdir()
    (layer_dir / "first/first.txt").touch()

    (layer_dir / "second").mkdir()
    (layer_dir / "second/second.txt").touch()
    # Add an opaque marker to signify that "second/" should hide the
    # base layer's "second" symlink.
    overlays.oci_opaque_dir(layer_dir / "second").touch()

    # Create a dir tree to act as extracted "base"
    # It contains a "first" dir and a "second" symlink pointing to "first"
    rootfs_dir = tmp_path / "rootfs"
    rootfs_dir.mkdir()

    (rootfs_dir / "first").mkdir()
    (rootfs_dir / "second").symlink_to("first")

    temp_tar_path = tmp_path / "layer.tar"
    layers.archive_layer(layer_dir, temp_tar_path, base_layer_dir=rootfs_dir)
    temp_tar_contents = get_tar_contents(temp_tar_path)

    # The tarfile *must* contain the "second" dir entry, because of the
    # opaque whiteout file.
    expected_tar_contents = [
        "first",
        "first/first.txt",
        "second",
        "second/.wh..wh..opq",
        "second/second.txt",
    ]
    assert sorted(temp_tar_contents) == expected_tar_contents


def test_archive_layer_with_base_layer_subdirs(tmp_path):
    """Test base layer handling with subdirectories."""
    layer_dir = tmp_path / "layer_dir"
    layer_dir.mkdir()

    # The path "second/" contains multiple subdirectories.
    (layer_dir / "second").mkdir()
    (layer_dir / "second/second.txt").touch()

    (layer_dir / "second/subdir").mkdir()
    (layer_dir / "second/subdir/subdir_file.txt").touch()

    (layer_dir / "second/subdir/subsubdir").mkdir()
    (layer_dir / "second/subdir/subsubdir/subsubdir_file.txt").touch()

    (layer_dir / "third").mkdir()
    (layer_dir / "third/third.txt").touch()

    rootfs_dir = tmp_path / "rootfs"
    rootfs_dir.mkdir()

    # The base layer has a "first/" dir and a symlink to it called "second".
    # Every subdirectory in "second/" in the "upper" layer must be added as
    # a subdir of "first".
    (rootfs_dir / "first").mkdir()
    (rootfs_dir / "second").symlink_to("first")

    temp_tar_path = tmp_path / "layer.tar"
    layers.archive_layer(layer_dir, temp_tar_path, base_layer_dir=rootfs_dir)
    temp_tar_contents = get_tar_contents(temp_tar_path)

    expected_tar_contents = [
        "first/second.txt",
        "first/subdir",
        "first/subdir/subdir_file.txt",
        "first/subdir/subsubdir",
        "first/subdir/subsubdir/subsubdir_file.txt",
        "third",
        "third/third.txt",
    ]
    assert temp_tar_contents == expected_tar_contents


def test_archive_layer_duplicate_dirs(tmp_path):
    """
    Test creating a layer where, because of symlinks in the base, multiple
    directories end up as the same target.
    """

    layer_dir, rootfs_dir = duplicate_dirs_setup(tmp_path)

    temp_tar_path = tmp_path / "layer.tar"
    layers.archive_layer(layer_dir, temp_tar_path, base_layer_dir=rootfs_dir)
    temp_tar_contents = get_tar_contents(temp_tar_path)

    expected_tar_contents = [
        "usr",
        "usr/bin",
        "usr/bin/dir1",
        "usr/bin/dir1/a.txt",
        "usr/bin/dir1/b.txt",
    ]
    assert temp_tar_contents == expected_tar_contents


def test_archive_layer_duplicate_dirs_conflict(tmp_path):
    """
    Test creating a layer where, because of symlinks in the base, multiple
    directories end up as the same target but the directories have different
    ownership/permissions.
    """
    layer_dir, rootfs_dir = duplicate_dirs_setup(tmp_path)

    # Change the default permissions of the directories that will end up as
    # "/usr/bin/dir1", to ensure that they are different.
    if sys.platform == "win32":
        # On Windows, chmod() can only change a directory's read-only status.
        (layer_dir / "bin/dir1").chmod(stat.S_IWRITE)
        (layer_dir / "usr/bin/dir1").chmod(stat.S_IREAD)
    else:
        (layer_dir / "bin/dir1").chmod(0o40770)
        (layer_dir / "usr/bin/dir1").chmod(0o40775)

    # Check that the error message show the conflicting paths.
    expected_message = (
        f"Conflicting paths pointing to '{Path('usr/bin/dir1')}': "
        f"{layer_dir / 'bin/dir1'}, "
        f"{layer_dir / 'usr/bin/dir1'}"
    )
    temp_tar_path = tmp_path / "layer.tar"
    with pytest.raises(errors.LayerArchivingError, match=re.escape(expected_message)):
        layers.archive_layer(layer_dir, temp_tar_path, base_layer_dir=rootfs_dir)


def test_archive_layer_duplicate_files(tmp_path):
    """
    Test creating a layer where, because of symlinks in the base, multiple
    files (not directories) end up at the same target. The files have different
    contents so this must raise an error.
    """
    layer_dir, rootfs_dir = duplicate_dirs_setup(tmp_path)

    # Create files with the same name but different contents in both
    # directories.
    (layer_dir / "bin/dir1/same.txt").write_text("first")
    (layer_dir / "usr/bin/dir1/same.txt").write_text("second")

    # Check that the error message show the conflicting paths.
    expected_message = (
        f"Conflicting paths pointing to '{Path('usr/bin/dir1/same.txt')}': "
        f"{layer_dir / 'bin/dir1/same.txt'}, "
        f"{layer_dir / 'usr/bin/dir1/same.txt'}"
    )
    temp_tar_path = tmp_path / "layer.tar"
    with pytest.raises(errors.LayerArchivingError, match=re.escape(expected_message)):
        layers.archive_layer(layer_dir, temp_tar_path, base_layer_dir=rootfs_dir)


def test_archive_layer_duplicate_identical_files(tmp_path):
    """
    Test creating a layer where, because of symlinks in the base, multiple
    files (not directories) end up at the same target. The files are identical
    so the layer must be created successfully.
    """
    layer_dir, rootfs_dir = duplicate_dirs_setup(tmp_path)

    # Create files with the same contents with the same name in both directories
    (layer_dir / "bin/dir1/same.txt").write_text("foobar")
    (layer_dir / "usr/bin/dir1/same.txt").write_text("foobar")

    temp_tar_path = tmp_path / "layer.tar"
    layers.archive_layer(layer_dir, temp_tar_path, base_layer_dir=rootfs_dir)
    temp_tar_contents = get_tar_contents(temp_tar_path)

    expected_tar_contents = [
        "usr",
        "usr/bin",
        "usr/bin/dir1",
        "usr/bin/dir1/a.txt",
        "usr/bin/dir1/b.txt",
        "usr/bin/dir1/same.txt",
    ]
    assert temp_tar_contents == expected_tar_contents


def test_prune_prime_files(tmp_path):
    base_layer_dir = tmp_path / "base"
    base_layer_dir.mkdir()

    (base_layer_dir / "file1.txt").write_text("file1")
    (base_layer_dir / "file2.txt").write_text("file2")
    (base_layer_dir / "file3.txt").write_text("file3")
    (base_layer_dir / "file3.txt").chmod(0o666)

    prime_dir = tmp_path / "prime"
    prime_dir.mkdir()

    # file1.txt is identical
    (prime_dir / "file1.txt").write_text("file1")
    # file2.txt has different contents
    (prime_dir / "file2.txt").write_text("different")
    # file3.txt has same contents but different permissions
    (prime_dir / "file3.txt").write_text("file3")
    (prime_dir / "file3.txt").chmod(0o444)

    files = {Path("file1.txt"), Path("file2.txt"), Path("file3.txt")}
    layers.prune_prime_files(prime_dir, files, base_layer_dir)

    # "file1.txt" gets pruned, the other files remain.
    assert sorted(os.listdir(prime_dir)) == ["file2.txt", "file3.txt"]  # noqa: PTH208 (use Path.iterdir())
