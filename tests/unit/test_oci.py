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
from pathlib import Path
from typing import NamedTuple
from unittest.mock import ANY, call, mock_open, patch

import pytest
from rockcraft import errors, oci
from rockcraft.architectures import SUPPORTED_ARCHS
from rockcraft.pebble import Pebble

import tests

MOCK_NEW_USER = {
    "user": "foo",
    "uid": 585287,
    "passwd": "foo:x:585287:585287::/var/lib/pebble/default:/usr/bin/false\n",
    "group": "foo:x:585287:\n",
    "shadow": str(
        "foo:!:"
        f"{(datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).days}"
        "::::::\n"
    ),
}


@pytest.fixture
def mock_run(mocker):
    return mocker.patch("rockcraft.oci._process_run")


@pytest.fixture
def mock_archive_layer(mocker):
    return mocker.patch("rockcraft.layers.archive_layer")


@pytest.fixture
def mock_rmtree(mocker):
    return mocker.patch("shutil.rmtree")


@pytest.fixture
def mock_mkdir(mocker):
    return mocker.patch("pathlib.Path.mkdir")


@pytest.fixture
def mock_mkdtemp(mocker):
    return mocker.patch("tempfile.mkdtemp")


@pytest.fixture
def mock_tmpdir(mocker):
    return mocker.patch("tempfile.TemporaryDirectory")


@pytest.fixture
def mock_inject_oci_fields(mocker):
    return mocker.patch("rockcraft.oci._inject_oci_fields")


@pytest.fixture
def mock_read_bytes(mocker):
    return mocker.patch("pathlib.Path.read_bytes")


@pytest.fixture
def mock_write_bytes(mocker):
    return mocker.patch("pathlib.Path.write_bytes")


@pytest.fixture
def mock_unlink(mocker):
    return mocker.patch("pathlib.Path.unlink")


@pytest.fixture
def mock_add_layer(mocker):
    return mocker.patch("rockcraft.oci.Image.add_layer")


@tests.linux_only
class TestImage:
    """OCI image manipulation."""

    def test_attributes(self):
        image = oci.Image("a:b", Path("/c"))
        assert image.image_name == "a:b"
        assert image.path == Path("/c")

    def test_from_docker_registry(self, mock_run, new_dir):
        image, source_image = oci.Image.from_docker_registry(
            "a@b", image_dir=Path("images/dir"), arch="amd64"
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
            "a@b", image_dir=Path("images/dir"), arch="arm64"
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

    def _get_arch_from_call(self, mock_call):
        class ArchData(NamedTuple):
            override_arch: str
            override_variant: str | None

        call_args = mock_call.args[0]
        override_arch_index = call_args.index("--override-arch")
        override_arch = call_args[override_arch_index + 1]

        override_variant = None
        try:
            override_variant_index = call_args.index("--override-variant")
            override_variant = call_args[override_variant_index + 1]
        except ValueError:
            pass

        return ArchData(override_arch, override_variant)

    # The archs here were taken from the supported architectures in the registry
    # that we currently use (https://gallery.ecr.aws/ubuntu/ubuntu)
    @pytest.mark.parametrize(
        ("deb_arch", "expected_arch", "expected_variant"),
        [
            ("amd64", "amd64", None),
            ("arm64", "arm64", "v8"),
            ("armhf", "arm", "v7"),
            ("ppc64el", "ppc64le", None),
            ("s390x", "s390x", None),
        ],
    )
    def test_from_docker_registry_arch(
        self, mock_run, new_dir, deb_arch, expected_arch, expected_variant
    ):
        """Test that the correct arch-related parameters are passed to skopeo."""
        oci.Image.from_docker_registry(
            "a@b", image_dir=Path("images/dir"), arch=deb_arch
        )
        arch_data = self._get_arch_from_call(mock_run.mock_calls[0])

        assert arch_data.override_arch == expected_arch
        assert arch_data.override_variant == expected_variant

    @pytest.mark.parametrize("deb_arch", list(SUPPORTED_ARCHS))
    def test_new_oci_image(self, mock_inject_oci_fields, mock_run, deb_arch):
        """Test that new blank images are created with the correct GOARCH values."""
        expected = SUPPORTED_ARCHS[deb_arch]

        image_dir = Path("images/dir")
        image, source_image = oci.Image.new_oci_image(
            "bare@latest", image_dir=image_dir, arch=deb_arch
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
                    expected.go_arch,
                    "--no-history",
                ]
            ),
        ]
        mock_inject_oci_fields.assert_called_once_with(
            image_dir / "bare:latest", arch_variant=expected.go_variant
        )

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
        mock_proc_run = mocker.patch("craft_parts.utils.process.run")
        image.add_layer("tag", Path("layer_dir"))

        expected_tar_file = new_dir / f"c/.temp_layer.{pid}.tar"
        expected_tar_cmd = [
            "tar",
            "-cf",
            expected_tar_file,
            "--no-recursion",
            "--acls",
            "--xattrs",
            "--selinux",
            Path("foo.txt"),
        ]
        mock_proc_run.assert_called_once_with(expected_tar_cmd, cwd=ANY, check=True)
        expected_cmd = [
            "umoci",
            "raw",
            "add-layer",
            "--image",
            str(new_dir / "c/a:b"),
            str(expected_tar_file),
            "--tag",
            "tag",
        ]
        mock_run.assert_called_once_with(
            [*expected_cmd, "--history.created_by", " ".join(expected_cmd)]
        )

    def test_add_new_user(
        self,
        check,
        mock_tmpdir,
        mock_add_layer,
        tmp_path,
    ):
        fake_tmpfs = tmp_path / "mock-tmp"
        mock_tmpdir.return_value.__enter__.return_value = str(fake_tmpfs)

        image = oci.Image("a:b", Path("/c"))
        image.add_user(
            tmp_path / "prime",
            tmp_path,
            "mock-tag",
            MOCK_NEW_USER["user"],
            MOCK_NEW_USER["uid"],
        )

        mock_tmpdir.assert_called_once()
        check.equal(
            (fake_tmpfs / "etc/passwd").read_text(),
            MOCK_NEW_USER["passwd"],
        )
        check.equal(
            (fake_tmpfs / "etc/group").read_text(),
            MOCK_NEW_USER["group"],
        )

        check.is_false((fake_tmpfs / "etc/shadow").exists())
        mock_add_layer.assert_called_once_with("mock-tag", fake_tmpfs)

        # Test with a conflicting user or ID.
        # Use the new fs as a base to force the error.
        with pytest.raises(errors.RockcraftError) as err:
            image.add_user(
                tmp_path / "prime",
                fake_tmpfs,
                "mock-tag",
                MOCK_NEW_USER["user"],
                MOCK_NEW_USER["uid"] + 1,
            )
        check.is_in(
            "conflict with existing user/group in the base filesystem", str(err)
        )

        with pytest.raises(errors.RockcraftError) as err:
            image.add_user(
                tmp_path / "prime",
                fake_tmpfs,
                "mock-tag",
                MOCK_NEW_USER["user"] + "bar",
                MOCK_NEW_USER["uid"],
            )
        check.is_in(
            "conflict with existing user/group in the base filesystem", str(err)
        )

    @pytest.mark.parametrize(
        (
            "base_user_files",
            "prime_user_files",
            "whiteouts_exist",
            "expected_user_files",
        ),
        [
            # If file in prime, the rest doesn't matter
            (
                {
                    "passwd": "someuser:x:10:10::/nonexistent:/usr/bin/false\n",
                    "group": "somegroup:x:10:\n",
                    "shadow": "somegroup:!:19369::::::\n",
                },
                {
                    "passwd": "primeuser:x:11:11::/nonexistent:/usr/bin/false\n",
                    "group": "primegroup:x:11:\n",
                    "shadow": "primegroup:!:19370::::::\n",
                },
                True,
                {
                    "passwd": str(
                        "primeuser:x:11:11::/nonexistent:/usr/bin/false\n"
                        f"{MOCK_NEW_USER['passwd']}"
                    ),
                    "group": f"primegroup:x:11:\n{MOCK_NEW_USER['group']}",
                    "shadow": f"primegroup:!:19370::::::\n{MOCK_NEW_USER['shadow']}",
                },
            ),
            # If file NOT in prime but in base, then take the base's data
            (
                {
                    "passwd": "someuser:x:10:10::/nonexistent:/usr/bin/false\n",
                    "group": "somegroup:x:10:\n",
                    "shadow": "somegroup:!:19369::::::\n",
                },
                {},
                False,
                {
                    "passwd": str(
                        "someuser:x:10:10::/nonexistent:/usr/bin/false\n"
                        f"{MOCK_NEW_USER['passwd']}"
                    ),
                    "group": f"somegroup:x:10:\n{MOCK_NEW_USER['group']}",
                    "shadow": f"somegroup:!:19369::::::\n{MOCK_NEW_USER['shadow']}",
                },
            ),
            # If file is removed in prime, then take an empty file
            # If "shadow" is removed or absent, then it's ignored
            (
                {
                    "passwd": "someuser:x:10:10::/nonexistent:/usr/bin/false\n",
                    "group": "somegroup:x:10:\n",
                    "shadow": "somegroup:!:19369::::::\n",
                },
                {},
                True,
                {
                    "passwd": str(f"{MOCK_NEW_USER['passwd']}"),
                    "group": MOCK_NEW_USER["group"],
                    "shadow": MOCK_NEW_USER["shadow"],
                },
            ),
        ],
    )
    def test_append_new_user(
        self,
        check,
        mock_tmpdir,
        mock_add_layer,
        tmp_path,
        base_user_files,
        prime_user_files,
        whiteouts_exist,
        expected_user_files,
    ):
        # Mock the existence of users, either in the base or the primed dir
        # tmp_path will be fake_base
        fake_prime = tmp_path / "prime"
        fake_prime_etc = fake_prime / "etc"
        fake_base_etc = tmp_path / "etc"
        fake_prime_etc.mkdir(parents=True, exist_ok=True)
        fake_base_etc.mkdir(parents=True, exist_ok=True)

        for filename in ["passwd", "group", "shadow"]:
            if base_user_files:
                (fake_base_etc / filename).write_text(base_user_files[filename])

            if prime_user_files:
                (fake_prime_etc / filename).write_text(prime_user_files[filename])

            if whiteouts_exist:
                (fake_prime_etc / f".wh.{filename}").touch()

        fake_tmp_new_layer = tmp_path / "mock-tmp"
        mock_tmpdir.return_value.__enter__.return_value = str(fake_tmp_new_layer)

        image = oci.Image("a:b", Path("/c"))
        image.add_user(
            fake_prime,
            tmp_path,
            "mock-tag",
            MOCK_NEW_USER["user"],
            MOCK_NEW_USER["uid"],
        )

        mock_tmpdir.assert_called_once()
        mock_add_layer.assert_called_once_with("mock-tag", fake_tmp_new_layer)
        check.equal(
            (fake_tmp_new_layer / "etc/passwd").read_text(),
            expected_user_files["passwd"],
        )
        check.equal(
            (fake_tmp_new_layer / "etc/group").read_text(),
            expected_user_files["group"],
        )
        if prime_user_files or not whiteouts_exist:
            check.equal(
                (fake_tmp_new_layer / "etc/shadow").read_text(),
                expected_user_files["shadow"],
            )

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
        mock_skopeo = mocker.patch(
            "shutil.which",
            return_value="/usr/bin/skopeo",
        )

        digest = image.digest(source_image)
        assert mock_skopeo.mock_calls == [call("skopeo")]
        assert mock_output.mock_calls == [
            call(
                [
                    "/usr/bin/skopeo",
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

        image.set_default_user(584792, "_daemon_")

        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--clear=config.entrypoint",
                    "--config.user",
                    "584792",
                ]
            )
        ]

    @pytest.mark.parametrize(
        ("entrypoint"),
        [
            ([Pebble.PEBBLE_BINARY_PATH_PREVIOUS, "enter"],),
            ([Pebble.PEBBLE_BINARY_PATH, "enter"],),
            (["echo", "Test"],),
            ([],),
        ],
    )
    def test_set_entrypoint_default(self, mock_run, entrypoint):
        image = oci.Image("a:b", Path("/tmp"))

        image.set_entrypoint(entrypoint)

        arg_list = [
            "umoci",
            "config",
            "--image",
            "/tmp/a:b",
            "--clear=config.entrypoint",
        ]

        for e in entrypoint:
            arg_list.extend(["--config.entrypoint", e])

        arg_list.append("--clear=config.cmd")

        assert mock_run.mock_calls == [
            call(arg_list),
        ]

    @pytest.mark.parametrize(("cmd"), [(["echo", "Test"]), ([])])
    def test_set_cmd(self, mock_run, cmd):
        image = oci.Image("a:b", Path("/c"))
        image.set_cmd(cmd)

        arg_list = [
            "umoci",
            "config",
            "--image",
            "/c/a:b",
            "--clear=config.cmd",
        ]

        for arg in cmd:
            arg_list.extend(["--config.cmd", arg])

        assert mock_run.mock_calls == [
            call(arg_list),
        ]

    @pytest.mark.parametrize(
        ("mock_services", "mock_checks"),
        [
            # Both services and checks are given
            (
                {
                    "mockServiceOne": {"override": "replace", "command": "foo"},
                    "mockServiceTwo": {"override": "merge", "command": "bar"},
                },
                {
                    "mockCheckOne": {
                        "http": {"url": "example.com"},
                        "override": "replace",
                    },
                    "mockCheckTwo": {"tcp": {"port": 1}, "override": "merge"},
                },
            ),
            # Only services are given
            (
                {
                    "mockServiceOne": {"override": "replace", "command": "foo"},
                    "mockServiceTwo": {"override": "merge", "command": "bar"},
                },
                {},
            ),
            # Only checks are given
            (
                {},
                {
                    "mockCheckOne": {
                        "http": {"url": "example.com"},
                        "override": "replace",
                    },
                    "mockCheckTwo": {"tcp": {"port": 1}, "override": "merge"},
                },
            ),
        ],
    )
    def test_set_pebble_layer(
        self,
        mock_services,
        mock_checks,
        mock_add_layer,
        mock_tmpdir,
        tmp_path,
        mocker,
    ):
        image = oci.Image("a:b", Path("/c"))

        mock_summary = "summary"
        mock_description = "description"

        expected_layer = {
            "summary": mock_summary,
            "description": mock_description,
        }

        if mock_services:
            expected_layer["services"] = mock_services
        if mock_checks:
            expected_layer["checks"] = mock_checks

        mock_name = "rock"
        mock_tag = "tag"
        mock_base_layer_dir = tmp_path / "base"
        mock_define_pebble_layer = mocker.patch(
            "rockcraft.pebble.Pebble.define_pebble_layer"
        )
        mock_define_pebble_layer.return_value = None

        fake_tmpfs = tmp_path / "mock-tmp-pebble-layer-path"
        mock_tmpdir.return_value.__enter__.return_value = str(fake_tmpfs)

        image.set_pebble_layer(
            mock_services,
            mock_checks,
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

    def test_set_environment(self, mock_run):
        image = oci.Image("a:b", Path("/c"))

        image.set_environment({"NAME1": "VALUE1", "NAME2": "VALUE2"})

        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--config.env",
                    "NAME1=VALUE1",
                    "--config.env",
                    "NAME2=VALUE2",
                ]
            )
        ]

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

        expected = (f"created: '{now}'" + "{n}name: rock-name{n}version: 1{n}").format(
            n=os.linesep
        )

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
            "/c/a:b",
            str(f"/c/.temp_layer.control_data.{os.getpid()}.tar"),
        ]
        assert mock_run.mock_calls == [
            call(
                [*expected_cmd, "--history.created_by", " ".join(expected_cmd)],
            )
        ]
        mock_rmtree.assert_called_once_with(Path(mock_control_data_path))

    def test_set_annotations(self, mocker):
        mocker.patch("rockcraft.utils.get_host_command").return_value = "umoci"
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
                text=True,
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
                text=True,
            ),
        ]

    def test_inject_oci_fields(self, mock_read_bytes, mock_write_bytes, mock_unlink):
        test_index = {
            "manifests": [
                {
                    "digest": "sha256:foomanifest",
                    "annotations": {
                        "org.opencontainers.image.ref.name": "latest",
                    },
                }
            ]
        }
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
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "config": {
                    "digest": f"sha256:{new_image_config_digest}",
                    "size": len(new_test_config_bytes),
                },
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
                        "annotations": {
                            "org.opencontainers.image.ref.name": "latest",
                        },
                        "size": len(new_test_manifest_bytes),
                    }
                ]
            },
        }

        # pylint: disable=protected-access
        oci._inject_oci_fields(Path("img:latest"), test_variant)
        assert mock_read_bytes.call_count == 3
        assert mock_write_bytes.mock_calls == [
            call(new_test_config_bytes),
            call(new_test_manifest_bytes),
            call(json.dumps(new_test_index).encode("utf-8")),
        ]
        assert mock_unlink.call_count == 2

    def test_stat(self, new_dir, mock_inject_oci_fields, mock_run, mocker):
        image_dir = Path("images/dir")
        mock_loads = mocker.patch("json.loads")

        image, _ = oci.Image.new_oci_image(
            "bare@latest", image_dir=image_dir, arch="amd64"
        )

        mock_run.reset_mock()

        image.stat()

        assert mock_inject_oci_fields.call_count == 1
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

    def test_get_manifest(self, new_dir, mock_inject_oci_fields, mock_run, mocker):
        image_dir = Path("images/dir")
        mock_loads = mocker.patch("json.loads")

        image, _ = oci.Image.new_oci_image(
            "bare@latest", image_dir=image_dir, arch="amd64"
        )

        mock_run.reset_mock()

        image.get_manifest()

        assert mock_run.mock_calls == [
            call(
                [
                    "skopeo",
                    "inspect",
                    "--raw",
                    "oci:images/dir/bare:latest",
                ]
            )
        ]
        assert mock_loads.called

    def test_set_path_bare(self, mock_run):
        image = oci.Image("a:b", Path("/c"))

        image.set_default_path("bare")

        expected = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--config.env",
                    f"PATH={expected}",
                ]
            )
        ]

    @pytest.mark.parametrize(
        "base",
        ["ubuntu@24.04", "ubuntu@22.04", "ubuntu@20.04"],
    )
    def test_set_path_non_bare(self, mock_run, base):
        image = oci.Image("a:b", Path("/c"))

        image.set_default_path(base)

        assert not mock_run.called
