# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021-2022 Canonical Ltd.
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

import datetime
import hashlib
import json
import os
import tarfile
from pathlib import Path
from typing import List, Tuple
from unittest.mock import ANY, call, mock_open, patch

import pytest
from craft_parts.overlays import overlays

import tests
from rockcraft import errors, oci


@pytest.fixture
def mock_run(mocker):
    yield mocker.patch("rockcraft.oci._process_run")


@pytest.fixture
def mock_archive_layer(mocker):
    yield mocker.patch("rockcraft.oci._archive_layer")


@pytest.fixture
def mock_rmtree(mocker):
    yield mocker.patch("shutil.rmtree")


@pytest.fixture
def mock_mkdir(mocker):
    yield mocker.patch("pathlib.Path.mkdir")


@pytest.fixture
def mock_mkdtemp(mocker):
    yield mocker.patch("tempfile.mkdtemp")


@pytest.fixture
def mock_tmpdir(mocker):
    yield mocker.patch("tempfile.TemporaryDirectory")


@pytest.fixture
def mock_inject_variant(mocker):
    yield mocker.patch("rockcraft.oci._inject_architecture_variant")


@pytest.fixture
def mock_read_bytes(mocker):
    yield mocker.patch("pathlib.Path.read_bytes")


@pytest.fixture
def mock_write_bytes(mocker):
    yield mocker.patch("pathlib.Path.write_bytes")


@pytest.fixture
def mock_add_layer(mocker):
    yield mocker.patch("rockcraft.oci.Image.add_layer")


@pytest.fixture
def temp_tar_contents(mocker) -> List[str]:
    """Fixture that mocks `oci._add_layer_into_image()` to inspect the temporary
    tarfile that is generated by `oci._archive_layer()`.

    :return: A list with the names of the files/directories in the "intercepted"
        tarfile.
    """
    contents = []

    def list_tar(_image_path: Path, archived_content: Path, **_kwargs):
        with tarfile.open(archived_content, "r") as tar_file:
            contents.extend(tar_file.getnames())

    mocker.patch.object(
        oci, "_add_layer_into_image", side_effect=list_tar, autospec=True
    )

    return contents


@tests.linux_only
class TestImage:
    """OCI image manipulation."""

    def test_attributes(self):
        image = oci.Image("a:b", Path("/c"))
        assert image.image_name == "a:b"
        assert image.path == Path("/c")

    def test_from_docker_registry(self, mock_run, new_dir):
        image, source_image = oci.Image.from_docker_registry(
            "a:b", image_dir=Path("images/dir"), arch="amd64", variant=None
        )
        assert Path("images/dir").is_dir()
        assert image.image_name == "a:b"
        assert source_image == f"docker://{oci.REGISTRY_URL}/a:b"
        assert image.path == Path("images/dir")
        assert mock_run.mock_calls == [
            call(
                [
                    "skopeo",
                    "--insecure-policy",
                    "--override-arch",
                    "amd64",
                    "copy",
                    "--retry-times",
                    str(oci.MAX_DOWNLOAD_RETRIES),
                    f"docker://{oci.REGISTRY_URL}/a:b",
                    "oci:images/dir/a:b",
                ]
            )
        ]
        mock_run.reset_mock()
        _ = oci.Image.from_docker_registry(
            "a:b", image_dir=Path("images/dir"), arch="arm64", variant="v8"
        )
        assert mock_run.mock_calls == [
            call(
                [
                    "skopeo",
                    "--insecure-policy",
                    "--override-arch",
                    "arm64",
                    "--override-variant",
                    "v8",
                    "copy",
                    "--retry-times",
                    str(oci.MAX_DOWNLOAD_RETRIES),
                    f"docker://{oci.REGISTRY_URL}/a:b",
                    "oci:images/dir/a:b",
                ]
            )
        ]

    def test_new_oci_image(self, mock_inject_variant, mock_run):
        image_dir = Path("images/dir")
        image, source_image = oci.Image.new_oci_image(
            "bare:latest", image_dir=image_dir, arch="amd64"
        )
        assert image_dir.is_dir()
        assert image.image_name == "bare:latest"
        assert source_image == f"oci:{str(image_dir)}/bare:latest"
        assert image.path == Path("images/dir")
        assert mock_run.mock_calls == [
            call(["umoci", "init", "--layout", f"{image_dir}/bare"]),
            call(["umoci", "new", "--image", f"{image_dir}/bare:latest"]),
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    f"{image_dir}/bare:latest",
                    "--architecture",
                    "amd64",
                    "--no-history",
                ]
            ),
        ]
        mock_inject_variant.assert_not_called()
        _ = oci.Image.new_oci_image(
            "bare:latest", image_dir=image_dir, arch="foo", variant="bar"
        )
        mock_inject_variant.assert_called_once_with(image_dir / "bare", "bar")

    def test_copy_to(self, mock_run):
        image = oci.Image("a:b", Path("/c"))
        new_image = image.copy_to("d:e", image_dir=Path("/f"))
        assert new_image.image_name == "d:e"
        assert new_image.path == Path("/f")
        assert mock_run.mock_calls == [
            call(
                [
                    "skopeo",
                    "--insecure-policy",
                    "copy",
                    "oci:/c/a:b",
                    "oci:/f/d:e",
                ]
            )
        ]

    def test_extract_to(self, mock_run, new_dir):
        image = oci.Image("a:b", Path("/c"))
        bundle_path = image.extract_to(Path("bundle/dir"))
        assert Path("bundle/dir").is_dir()
        assert bundle_path == Path("bundle/dir/a-b/rootfs")
        assert mock_run.mock_calls == [
            call(["umoci", "unpack", "--image", "/c/a:b", "bundle/dir/a-b"])
        ]

    def test_extract_to_rootless(self, mock_run, new_dir):
        image = oci.Image("a:b", Path("/c"))
        bundle_path = image.extract_to(Path("bundle/dir"), rootless=True)
        assert Path("bundle/dir").is_dir()
        assert bundle_path == Path("bundle/dir/a-b/rootfs")
        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "unpack",
                    "--rootless",
                    "--image",
                    "/c/a:b",
                    "bundle/dir/a-b",
                ]
            )
        ]

    def test_extract_to_existing_dir(self, mock_run, new_dir):
        image = oci.Image("a:b", Path("c"))
        Path("bundle/dir/a-b").mkdir(parents=True)
        Path("bundle/dir/a-b/foo.txt").touch()

        bundle_path = image.extract_to(Path("bundle/dir"))
        assert Path("bundle/dir/a-b/foo.txt").exists() is False
        assert bundle_path == Path("bundle/dir/a-b/rootfs")

    def test_add_layer(self, mocker, mock_run, new_dir):
        image = oci.Image("a:b", new_dir / "c")
        Path("c").mkdir()
        Path("layer_dir").mkdir()
        Path("layer_dir/foo.txt").touch()
        pid = os.getpid()

        spy_add = mocker.spy(tarfile.TarFile, "add")

        image.add_layer("tag", Path("layer_dir"))
        # The `Tarfile.add()` on the directory ends up calling the method multiple
        # times (due to the recursion), but we're mainly interested that the first
        # call was to add `layer_dir`.
        assert spy_add.mock_calls[0] == call(
            ANY, Path("layer_dir/foo.txt"), arcname="foo.txt", recursive=False
        )

        expected_cmd = [
            "umoci",
            "raw",
            "add-layer",
            "--image",
            str(new_dir / "c/a:b"),
            str(new_dir / f"c/.temp_layer.{pid}.tar"),
            "--tag",
            "tag",
        ]
        assert mock_run.mock_calls == [
            call(expected_cmd + ["--history.created_by", " ".join(expected_cmd)])
        ]

    def test_add_layer_directories(self, tmp_path, temp_tar_contents):
        """Test that adding a directory as a layer explicitly preserves subdirs"""
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        layer_dir = tmp_path / "layer_dir"
        layer_dir.mkdir()

        (layer_dir / "first").mkdir()
        (layer_dir / "first/first.txt").touch()

        (layer_dir / "second").mkdir()
        (layer_dir / "second/second.txt").touch()

        image = oci.Image("a:b", dest_dir)

        assert len(temp_tar_contents) == 0
        image.add_layer("tag", layer_dir)

        expected_tar_contents = [
            "first",
            "first/first.txt",
            "second",
            "second/second.txt",
        ]
        assert temp_tar_contents == expected_tar_contents

    def test_add_layer_symlinks(self, tmp_path, temp_tar_contents):
        """
        Test creating a new layer with symlinks (both file and dir).
        """
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        layer_dir = tmp_path / "layer_dir"
        layer_dir.mkdir()

        (layer_dir / "first_dir").mkdir()
        (layer_dir / "first_file").touch()

        (layer_dir / "second_dir").symlink_to("first_dir", target_is_directory=True)
        (layer_dir / "second_file").symlink_to("first_file", target_is_directory=False)

        image = oci.Image("a:b", dest_dir)

        assert len(temp_tar_contents) == 0
        image.add_layer("tag", layer_dir)

        expected_tar_contents = [
            "first_dir",
            "first_file",
            "second_dir",
            "second_file",
        ]
        assert temp_tar_contents == expected_tar_contents

    def test_add_layer_with_base_layer_dir(self, tmp_path, temp_tar_contents):
        """Test creating a layer with a base layer dir for reference."""
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        layer_dir = tmp_path / "layer_dir"
        layer_dir.mkdir()

        (layer_dir / "first").mkdir()
        (layer_dir / "first/first.txt").touch()

        (layer_dir / "second").mkdir()
        (layer_dir / "second/second.txt").touch()

        image = oci.Image("a:b", dest_dir)

        # Create a dir tree to act as extracted "base"
        # It contains a "first" dir and a "second" symlink pointing to "first"
        rootfs_dir = tmp_path / "rootfs"
        rootfs_dir.mkdir()

        (rootfs_dir / "first").mkdir()
        (rootfs_dir / "second").symlink_to("first")

        assert len(temp_tar_contents) == 0
        image.add_layer("tag", layer_dir, base_layer_dir=rootfs_dir)

        # The tarfile must *not* contain the "./second" dir entry, to preserve
        # the base layer symlink. Additionally, the file "second.txt" must
        # be listed as inside "first/", and not "second/".
        expected_tar_contents = [
            "first",
            "first/first.txt",
            "first/second.txt",
        ]
        assert temp_tar_contents == expected_tar_contents

    def test_add_layer_with_base_layer_dir_opaque(self, tmp_path, temp_tar_contents):
        """
        Test creating a layer with a base layer dir for reference, but the new
        layer hides one of the dirs in the base layer via an opaque whiteout file.
        """
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        layer_dir = tmp_path / "layer_dir"
        layer_dir.mkdir()

        (layer_dir / "first").mkdir()
        (layer_dir / "first/first.txt").touch()

        (layer_dir / "second").mkdir()
        (layer_dir / "second/second.txt").touch()
        # Add an opaque marker to signify that "second/" should hide the
        # base layer's "second" symlink.
        overlays.oci_opaque_dir(layer_dir / "second").touch()

        image = oci.Image("a:b", dest_dir)

        # Create a dir tree to act as extracted "base"
        # It contains a "first" dir and a "second" symlink pointing to "first"
        rootfs_dir = tmp_path / "rootfs"
        rootfs_dir.mkdir()

        (rootfs_dir / "first").mkdir()
        (rootfs_dir / "second").symlink_to("first")

        assert len(temp_tar_contents) == 0
        image.add_layer("tag", layer_dir, base_layer_dir=rootfs_dir)

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

    def test_add_layer_with_base_layer_subdirs(self, tmp_path, temp_tar_contents):
        """Test base layer handling with subdirectories."""
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

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

        image = oci.Image("a:b", dest_dir)

        rootfs_dir = tmp_path / "rootfs"
        rootfs_dir.mkdir()

        # The base layer has a "first/" dir and a symlink to it called "second".
        # Every subdirectory in "second/" in the "upper" layer must be added as
        # a subdir of "first".
        (rootfs_dir / "first").mkdir()
        (rootfs_dir / "second").symlink_to("first")

        assert len(temp_tar_contents) == 0
        image.add_layer("tag", layer_dir, base_layer_dir=rootfs_dir)

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

    @staticmethod
    def _duplicate_dirs_setup(tmp_path) -> Tuple[Path, Path]:
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

    def test_add_layer_duplicate_dirs(self, tmp_path, temp_tar_contents):
        """
        Test creating a layer where, because of symlinks in the base, multiple
        directories end up as the same target.
        """
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        layer_dir, rootfs_dir = self._duplicate_dirs_setup(tmp_path)

        image = oci.Image("a:b", dest_dir)
        image.add_layer("tag", layer_dir, base_layer_dir=rootfs_dir)

        expected_tar_contents = [
            "usr",
            "usr/bin",
            "usr/bin/dir1",
            "usr/bin/dir1/a.txt",
            "usr/bin/dir1/b.txt",
        ]
        assert temp_tar_contents == expected_tar_contents

    def test_add_layer_duplicate_dirs_conflict(self, tmp_path, temp_tar_contents):
        """
        Test creating a layer where, because of symlinks in the base, multiple
        directories end up as the same target but the directories have different
        ownership/permissions.
        """
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        layer_dir, rootfs_dir = self._duplicate_dirs_setup(tmp_path)

        # Change the default permissions of the directories that will end up as
        # "/usr/bin/dir1", to ensure that they are different.
        (layer_dir / "bin/dir1").chmod(0o40770)
        (layer_dir / "usr/bin/dir1").chmod(0o40775)

        image = oci.Image("a:b", dest_dir)

        # Check that the error message show the conflicting paths.
        expected_message = (
            "Conflicting paths pointing to 'usr/bin/dir1': "
            f"{str(layer_dir / 'bin/dir1')}, "
            f"{str(layer_dir / 'usr/bin/dir1')}"
        )
        with pytest.raises(errors.LayerArchivingError, match=expected_message):
            image.add_layer("tag", layer_dir, base_layer_dir=rootfs_dir)

    def test_add_layer_duplicate_files(self, tmp_path, temp_tar_contents):
        """
        Test creating a layer where, because of symlinks in the base, multiple
        files (not directories) end up at the same target. The files have different
        contents so this must raise an error.
        """
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        layer_dir, rootfs_dir = self._duplicate_dirs_setup(tmp_path)

        # Create files with the same name but different contents in both
        # directories.
        (layer_dir / "bin/dir1/same.txt").write_text("first")
        (layer_dir / "usr/bin/dir1/same.txt").write_text("second")

        image = oci.Image("a:b", dest_dir)

        # Check that the error message show the conflicting paths.
        expected_message = (
            "Conflicting paths pointing to 'usr/bin/dir1/same.txt': "
            f"{str(layer_dir / 'bin/dir1/same.txt')}, "
            f"{str(layer_dir / 'usr/bin/dir1/same.txt')}"
        )
        with pytest.raises(errors.LayerArchivingError, match=expected_message):
            image.add_layer("tag", layer_dir, base_layer_dir=rootfs_dir)

    def test_add_new_user(
        self,
        check,
        mock_add_layer,
        mock_tmpdir,
        tmp_path,
    ):
        mock_tag = "tag"
        fake_tmpfs = tmp_path / "mock-tmp"
        mock_tmpdir.return_value = fake_tmpfs

        image = oci.Image("a:b", Path("/c"))
        image.add_user(tmp_path, mock_tag, "foo", 585287)

        mock_tmpdir.assert_called_once()
        check.equal(
            (fake_tmpfs / "etc/passwd").read_text(),
            "foo:x:585287:585287::/var/lib/pebble/default:/usr/bin/false\n",
        )
        check.equal((fake_tmpfs / "etc/group").read_text(), "foo:x:585287:\n")

        check.is_false(os.path.exists(fake_tmpfs / "etc/shadow"))
        mock_add_layer.assert_called_once_with(mock_tag, fake_tmpfs)

    def test_append_new_user(
        self,
        check,
        mock_add_layer,
        mock_tmpdir,
        tmp_path,
    ):
        # Mock the existence of users in the base image
        fake_etc = tmp_path / "etc"
        fake_etc.mkdir(parents=True, exist_ok=True)
        (fake_etc / "passwd").write_text(
            "someuser:x:10:10::/nonexistent:/usr/bin/false\n"
        )
        (fake_etc / "group").write_text("somegroup:x:10:\n")
        (fake_etc / "shadow").write_text("somegroup:!:19369::::::\n")

        mock_tag = "tag"
        fake_tmpfs = tmp_path / "mock-tmp"
        mock_tmpdir.return_value = fake_tmpfs

        image = oci.Image("a:b", Path("/c"))
        days_since_epoch = (
            datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        ).days
        image.add_user(tmp_path, mock_tag, "foo", 585287)

        mock_tmpdir.assert_called_once()
        check.equal(
            (fake_tmpfs / "etc/passwd").read_text(),
            str(
                "someuser:x:10:10::/nonexistent:/usr/bin/false\n"
                "foo:x:585287:585287::/var/lib/pebble/default:/usr/bin/false\n"
            ),
        )
        check.equal(
            (fake_tmpfs / "etc/group").read_text(),
            "somegroup:x:10:\nfoo:x:585287:\n",
        )
        check.equal(
            (fake_tmpfs / "etc/shadow").read_text(),
            f"somegroup:!:19369::::::\nfoo:!:{days_since_epoch}::::::\n",
        )

        mock_add_layer.assert_called_once_with(mock_tag, fake_tmpfs)

        # Test with a conflicting user or ID
        with pytest.raises(errors.RockcraftError) as err:
            image.add_user(tmp_path, mock_tag, "foo2", 10)
            check.is_in("conflict with existing user/group in the base filesystem", err)

        with pytest.raises(errors.RockcraftError) as err:
            image.add_user(tmp_path, mock_tag, "someuser", 585281)
            check.is_in("conflict with existing user/group in the base filesystem", err)

    def test_add_layer_duplicate_identical_files(self, tmp_path, temp_tar_contents):
        """
        Test creating a layer where, because of symlinks in the base, multiple
        files (not directories) end up at the same target. The files are identical
        so the layer must be created successfully.
        """
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        layer_dir, rootfs_dir = self._duplicate_dirs_setup(tmp_path)

        # Create files with the same contents with the same name in both directories
        (layer_dir / "bin/dir1/same.txt").write_text("foobar")
        (layer_dir / "usr/bin/dir1/same.txt").write_text("foobar")

        image = oci.Image("a:b", dest_dir)
        image.add_layer("tag", layer_dir, base_layer_dir=rootfs_dir)

        expected_tar_contents = [
            "usr",
            "usr/bin",
            "usr/bin/dir1",
            "usr/bin/dir1/a.txt",
            "usr/bin/dir1/b.txt",
            "usr/bin/dir1/same.txt",
        ]
        assert temp_tar_contents == expected_tar_contents

    def test_to_docker_daemon(self, mock_run):
        image = oci.Image("a:b", Path("/c"))
        image.to_docker_daemon("tag")
        assert mock_run.mock_calls == [
            call(
                [
                    "skopeo",
                    "--insecure-policy",
                    "copy",
                    "oci:/c/a:tag",
                    "docker-daemon:a:tag",
                ]
            )
        ]

    def test_to_oci_archive(self, mock_run):
        image = oci.Image("a:b", Path("/c"))
        image.to_oci_archive("tag", filename="foobar")
        assert mock_run.mock_calls == [
            call(
                [
                    "skopeo",
                    "--insecure-policy",
                    "copy",
                    "oci:/c/a:tag",
                    "oci-archive:foobar:tag",
                ]
            )
        ]

    def test_digest(self, mocker):
        source_image = "docker://ubuntu:22.04"
        image = oci.Image("a:b", Path("/c"))
        mock_output = mocker.patch(
            "subprocess.check_output",
            return_value="000102030405060708090a0b0c0d0e0f",
        )

        digest = image.digest(source_image)
        assert mock_output.mock_calls == [
            call(
                [
                    "skopeo",
                    "inspect",
                    "--format",
                    "{{.Digest}}",
                    "-n",
                    source_image,
                ],
                text=True,
            )
        ]
        assert digest == bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

    def test_set_default_user(self, mock_run):
        image = oci.Image("a:b", Path("/c"))

        image.set_default_user("foo")

        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--clear=config.entrypoint",
                    "--config.user",
                    "foo",
                ]
            )
        ]

    def test_set_entrypoint(self, mock_run):
        image = oci.Image("a:b", Path("/c"))

        image.set_entrypoint()

        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--clear=config.entrypoint",
                    "--config.entrypoint",
                    "/bin/pebble",
                    "--config.entrypoint",
                    "enter",
                    "--config.entrypoint",
                    "--verbose",
                ],
            ),
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--clear=config.cmd",
                ]
            ),
        ]

    def test_set_env(self, mocker):
        mock_run = mocker.patch("subprocess.run")
        image = oci.Image("a:b", Path("/c"))

        image.set_env([{"NAME1": "VALUE1"}, {"NAME2": "VALUE2"}])

        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--clear=config.env",
                    "--config.env",
                    "NAME1=VALUE1",
                    "--config.env",
                    "NAME2=VALUE2",
                ],
                capture_output=True,
                check=True,
                universal_newlines=True,
            )
        ]

    def test_set_pebble_services(
        self,
        mock_add_layer,
        mock_tmpdir,
        tmp_path,
        mocker,
    ):
        image = oci.Image("a:b", Path("/c"))

        mock_summary = "summary"
        mock_description = "description"
        mock_services = {
            "mockServiceOne": {"override": "replace", "command": "foo"},
            "mockServiceTwo": {"override": "merge", "command": "bar"},
        }
        expected_layer = {
            "summary": mock_summary,
            "description": mock_description,
            "services": mock_services,
        }

        mock_name = "rock"
        mock_tag = "tag"
        mock_base_layer_dir = tmp_path / "base"
        mock_define_pebble_layer = mocker.patch(
            "rockcraft.pebble.Pebble.define_pebble_layer"
        )
        mock_define_pebble_layer.return_value = None

        fake_tmpfs = tmp_path / "mock-tmp-pebble-layer-path"
        mock_tmpdir.return_value = fake_tmpfs

        image.set_pebble_services(
            mock_services,
            mock_name,
            mock_tag,
            mock_summary,
            mock_description,
            mock_base_layer_dir,
        )

        mock_tmpdir.assert_called_once()
        mock_add_layer.assert_called_once_with(mock_tag, fake_tmpfs)
        mock_define_pebble_layer.assert_called_once_with(
            fake_tmpfs, mock_base_layer_dir, expected_layer, mock_name
        )

    def test_set_control_data(
        self,
        mock_archive_layer,
        mock_rmtree,
        mock_mkdir,
        mock_mkdtemp,
        mock_run,
    ):
        image = oci.Image("a:b", Path("/c"))

        mock_control_data_path = "layer_dir"
        mock_mkdtemp.return_value = mock_control_data_path

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        metadata = {"name": "rock-name", "version": 1, "created": now}

        expected = (
            f"created: '{now}'" + "{n}" "name: rock-name{n}" "version: 1{n}"
        ).format(n=os.linesep)

        mocked_data = {"writes": ""}

        def mock_write(s):
            mocked_data["writes"] += s

        m = mock_open()
        with patch("pathlib.Path.open", m):
            with patch("pathlib.Path.chmod") as local_mock_chmod:
                m.return_value.write = mock_write
                image.set_control_data(metadata)

        local_mock_chmod.assert_called_once_with(0o644)
        assert mocked_data["writes"] == expected
        mock_mkdtemp.assert_called_once()
        mock_mkdir.assert_called_once()
        mock_archive_layer.assert_called_once_with(
            Path(mock_control_data_path),
            Path(f"/c/.temp_layer.control_data.{os.getpid()}.tar"),
        )
        expected_cmd = [
            "umoci",
            "raw",
            "add-layer",
            "--image",
            str("/c/a:b"),
            str(f"/c/.temp_layer.control_data.{os.getpid()}.tar"),
        ]
        assert mock_run.mock_calls == [
            call(
                expected_cmd + ["--history.created_by", " ".join(expected_cmd)],
            )
        ]
        mock_rmtree.assert_called_once_with(Path(mock_control_data_path))

    def test_set_annotations(self, mocker):
        mock_run = mocker.patch("subprocess.run")
        image = oci.Image("a:b", Path("/c"))

        image.set_annotations({"NAME1": "VALUE1", "NAME2": "VALUE2"})

        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--clear=config.labels",
                    "--config.label",
                    "NAME1=VALUE1",
                    "--config.label",
                    "NAME2=VALUE2",
                ],
                capture_output=True,
                check=True,
                universal_newlines=True,
            ),
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--clear=manifest.annotations",
                    "--manifest.annotation",
                    "NAME1=VALUE1",
                    "--manifest.annotation",
                    "NAME2=VALUE2",
                ],
                capture_output=True,
                check=True,
                universal_newlines=True,
            ),
        ]

    def test_inject_architecture_variant(self, mock_read_bytes, mock_write_bytes):
        test_index = {"manifests": [{"digest": "sha256:foomanifest"}]}
        test_manifest = {"config": {"digest": "sha256:fooconfig"}}
        test_config = {}
        mock_read_bytes.side_effect = [
            json.dumps(test_index),
            json.dumps(test_manifest),
            json.dumps(test_config),
        ]
        test_variant = "v0"

        new_test_config = {**test_config, **{"variant": test_variant}}
        new_test_config_bytes = json.dumps(new_test_config).encode("utf-8")

        new_image_config_digest = hashlib.sha256(new_test_config_bytes).hexdigest()
        new_test_manifest = {
            **test_manifest,
            **{
                "config": {
                    "digest": f"sha256:{new_image_config_digest}",
                    "size": len(new_test_config_bytes),
                }
            },
        }
        new_test_manifest_bytes = json.dumps(new_test_manifest).encode("utf-8")
        new_test_manifest_digest = hashlib.sha256(new_test_manifest_bytes).hexdigest()

        new_test_index = {
            **test_index,
            **{
                "manifests": [
                    {
                        "digest": f"sha256:{new_test_manifest_digest}",
                        "size": len(new_test_manifest_bytes),
                    }
                ]
            },
        }

        # pylint: disable=protected-access
        oci._inject_architecture_variant(Path("img"), test_variant)
        assert mock_read_bytes.call_count == 3
        assert mock_write_bytes.mock_calls == [
            call(new_test_config_bytes),
            call(new_test_manifest_bytes),
            call(json.dumps(new_test_index).encode("utf-8")),
        ]

    def test_archive_layer(self, mocker, new_dir):
        Path("layer_dir").mkdir()
        Path("layer_dir/bar.txt").touch()

        spy_add = mocker.spy(tarfile.TarFile, "add")

        oci._archive_layer(  # pylint: disable=protected-access
            Path("layer_dir"), Path("./bar.tar")
        )
        assert spy_add.call_count == 1

    def test_stat(self, new_dir, mock_run, mocker):
        image_dir = Path("images/dir")
        image, _ = oci.Image.new_oci_image(
            "bare:latest", image_dir=image_dir, arch="amd64"
        )

        mock_loads = mocker.patch("json.loads")
        mock_run.reset_mock()

        image.stat()

        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "stat",
                    "--json",
                    "--image",
                    "images/dir/bare:latest",
                ]
            )
        ]
        assert mock_loads.called
