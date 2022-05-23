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

from email.mime import base
import os
import tarfile
from datetime import datetime
from pathlib import Path
from unittest.mock import ANY, call, mock_open, patch

import pytest
import rockcraft
from rockcraft.errors import ConfigurationError
from rockcraft.project import UserInfo, UserAccount

import tests
from rockcraft import oci


@pytest.fixture
def mock_run(mocker):
    yield mocker.patch("rockcraft.oci._process_run")


@tests.linux_only
class TestImage:
    """OCI image manipulation."""

    @pytest.mark.parametrize(
        "user,uid,expected_output",
        [
            ("jon", 331, ("jon", 331)),
            ("jon", None, ("jon", 3)),
        ],
    )
    def test__sanitize_new_user(self, user, uid, expected_output):
        existing_users = ["foo", "bar"]
        existing_uids = [1, 2]
        uid_range = range(3, 4)

        assert oci.Image._sanitize_new_user(existing_users, existing_uids,
                                            user, uid, uid_range) == expected_output

    def test__sanitize_new_user_conflict(self):
        existing_users = ["foo", "bar"]
        existing_uids = [1, 2]
        uid_range = range(1, 3)

        with pytest.raises(ConfigurationError):
            oci.Image._sanitize_new_user(existing_users, existing_uids, "foo", 111)

        with pytest.raises(ConfigurationError):
            oci.Image._sanitize_new_user(existing_users, existing_uids, "newfoo", 1)

        with pytest.raises(ConfigurationError):
            oci.Image._sanitize_new_user(existing_users, existing_uids, "newfoo", None, uid_range)

    @pytest.mark.parametrize(
        "group,gid,expected_output",
        [
            ("gjon", 331, ("gjon", 331)),
            ("gjon", None, ("gjon", 3)),
            (None, 5, ('unnamedgroup5', 5)),
            (None, None, ('unnamedgroup3', 3)),
            ("foo", None, ("foo", 1)),
            (None, 2, ("bar", 2)),
            ("bar", 2, ("bar", 2)),
        ],
    )
    def test__sanitize_new_group(self, group, gid, expected_output):
        existing_groups = ["foo", "bar"]
        existing_gids = [1, 2]
        gid_range = range(3, 4)

        assert oci.Image._sanitize_new_group(existing_groups, existing_gids,
                                             group, gid, gid_range) == expected_output

    def test__sanitize_new_group_conflict(self):
        existing_groups = ["foo", "bar"]
        existing_gids = [1, 2]

        with pytest.raises(ConfigurationError):
            oci.Image._sanitize_new_group(existing_groups, existing_gids, "otherfoo", 1)

    def test__sanitize_new_user_info(self):
        user_info = {
            "full-name": "John Doe",
            "room-number": "0",
            "work-phone": "54321",
            "home-phone": "12345",
            "other": "comments"
        }

        assert oci.Image._sanitize_new_user_info(rockcraft.project.UserInfo(**user_info)) == tuple(user_info.values())

    @patch("rockcraft.oci._insert_into_image")
    @patch("os.mkdir")
    @patch("os.path.exists")
    def test__sanitize_new_user_home(self, mock_exists, mock_mkdir, mock_insert_into_image):
        # If home dir already exists, just return it back
        mock_exists.return_value = True
        image = oci.Image("a:b", Path("/c"))
        assert image._sanitize_new_user_home(None, Path('')) == '/nonexistent'
        assert image._sanitize_new_user_home(Path('/my_home'), Path('')) == '/my_home'
        assert len(mock_exists.mock_calls) == 2
        mock_mkdir.assert_not_called()
        mock_insert_into_image.assert_not_called()

        # otherwise, create it
        mock_exists.return_value = False
        assert image._sanitize_new_user_home(Path('/my_home'), Path('')) == '/my_home'
        mock_mkdir.assert_called_with(Path('') / 'my_home')
        mock_insert_into_image.assert_called_with(image.path / image.image_name, Path('') / 'my_home', Path('/my_home'))

    def test_attributes(self):
        image = oci.Image("a:b", Path("/c"))
        assert image.image_name == "a:b"
        assert image.path == Path("/c")

    def test_from_docker_registry(self, mock_run, new_dir):
        image = oci.Image.from_docker_registry("a:b", image_dir=Path("images/dir"))
        assert Path("images/dir").is_dir()
        assert image.image_name == "a:b"
        assert image.path == Path("images/dir")
        assert mock_run.mock_calls == [
            call(
                [
                    "skopeo",
                    "--insecure-policy",
                    "copy",
                    "docker://a:b",
                    "oci:images/dir/a:b",
                ]
            )
        ]

    def test_copy_to(self, mock_run):
        image = oci.Image("a:b", Path("/c"))
        new_image = image.copy_to("d:e", image_dir=Path("/f"))
        assert new_image.image_name == "d:e"
        assert new_image.path == Path("/f")
        assert mock_run.mock_calls == [
            call(["skopeo", "--insecure-policy", "copy", "oci:/c/a:b", "oci:/f/d:e"])
        ]

    def test_extract_to(self, mock_run, new_dir):
        image = oci.Image("a:b", Path("/c"))
        bundle_path = image.extract_to(Path("bundle/dir"))
        assert Path("bundle/dir").is_dir()
        assert bundle_path == Path("bundle/dir/a-b/rootfs")
        assert mock_run.mock_calls == [
            call(["umoci", "unpack", "--image", "/c/a:b", "bundle/dir/a-b"])
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
        assert spy_add.mock_calls == [call(ANY, "./foo.txt")]
        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "raw",
                    "add-layer",
                    "--tag",
                    "tag",
                    "--image",
                    str(new_dir / "c/a:b"),
                    str(new_dir / f"c/.temp_layer.{pid}.tar"),
                ]
            )
        ]

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
        image = oci.Image("a:b", Path("/c"))
        mock_output = mocker.patch(
            "subprocess.check_output", return_value="000102030405060708090a0b0c0d0e0f"
        )

        digest = image.digest()
        assert mock_output.mock_calls == [
            call(
                ["skopeo", "inspect", "--format", "{{.Digest}}", "oci:/c/a:b"],
                text=True,
            )
        ]
        assert digest == bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

    def test_set_entrypoint(self, mocker):
        mock_run = mocker.patch("subprocess.run")
        image = oci.Image("a:b", Path("/c"))

        image.set_entrypoint(["arg1", "arg2"])

        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--clear=config.entrypoint",
                    "--config.entrypoint",
                    "arg1",
                    "--config.entrypoint",
                    "arg2",
                ],
                capture_output=True,
                check=True,
                universal_newlines=True,
            )
        ]

    def test_set_cmd(self, mocker):
        mock_run = mocker.patch("subprocess.run")
        image = oci.Image("a:b", Path("/c"))

        image.set_cmd(["arg1", "arg2"])

        assert mock_run.mock_calls == [
            call(
                [
                    "umoci",
                    "config",
                    "--image",
                    "/c/a:b",
                    "--clear=config.cmd",
                    "--config.cmd",
                    "arg1",
                    "--config.cmd",
                    "arg2",
                ],
                capture_output=True,
                check=True,
                universal_newlines=True,
            )
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

    @patch('rockcraft.oci._config_image')
    def test_set_default_user(self, mock_config_img):
        image = oci.Image("a:b", Path("/c"))

        image.set_default_user("foo")

        assert mock_config_img.mock_calls == [
            call(
                image.path / image.image_name,
                ["--config.user", "foo"]
            )
        ]

    @patch('os.path.exists')
    @patch('rockcraft.oci.Image._sanitize_new_user_home')
    @patch('rockcraft.utils.extract_values_from_file')
    def test_create_users(self, mock_extractor, mock_sanitize_home, mock_exists):
        image = oci.Image("a:b", Path("/c"))
        base_rootfs_path = Path('/rootfs')
        mock_sanitize_home.return_value = '/my_home'
        days_since_epoch = (datetime.utcnow() - datetime(1970, 1, 1)).days
        mock_extractor.side_effect = [
            ["foo", "bar"],
            [1, 2]
        ]

        users_input = [
            UserAccount(**{
                'username': 'foo:1',
                'group': 'foogroup:1',
                'user-info': UserInfo(),
                'command': '/bin/bash'
            }),
            UserAccount(**{
                'username': 'new_bar:2',
                'group': 'bargroup:2',
                'user-info': UserInfo(),
            })
        ]
        
        # because "foo" already exists, get an error
        with pytest.raises(ConfigurationError):
            image.create_users(users_input, base_rootfs_path)

        existing_users_groups = (
            [["other-foo", "bar"], [11, 22]],
            [["other-foog", "barg"], [111, 222]]
        )
        mock_extractor.side_effect = existing_users_groups
        
        mock_exists.return_value = False  # /etc/shadow not in base
        m = mock_open()
        with patch("builtins.open", m):
            
            assert image.create_users(users_input, base_rootfs_path) == [base_rootfs_path / 'etc/passwd',
                                                                         base_rootfs_path / 'etc/group']

            assert m.call_count == 2
            
            mock_exists.return_value = True  # /etc/shadow in base
            m.reset_mock()
            # TODO: should avoid defining this side effect again
            mock_extractor.side_effect = (
                [["other-foo", "bar"], [11, 22]],
                [["other-foog", "barg"], [111, 222]]
            )
            assert image.create_users(users_input, base_rootfs_path) == [base_rootfs_path / 'etc/passwd',
                                                                         base_rootfs_path / 'etc/group',
                                                                         base_rootfs_path / 'etc/shadow']
            
            assert m().write.mock_calls == [
                call(
                    'foo:x:1:1:,,,,:/my_home:/bin/bash\nnew_bar:x:2:2:,,,,:/my_home:/usr/sbin/nologin\n'
                ),
                call(
                    'foogroup:x:1:\nbargroup:x:2:\n'
                ),
                call(
                    f'foo:*:{days_since_epoch}:0:99999:7:::\nnew_bar:*:{days_since_epoch}:0:99999:7:::\n'
                )
            ]
            
        # if trying to create two user accounts with the same username, should also fail
        users_input.append(UserAccount(**{'username': 'foo:2'}))
        # TODO: same duplication issue as above
        mock_extractor.side_effect = (
            [["other-foo", "bar"], [11, 22]],
            [["other-foog", "barg"], [111, 222]]
        )
        with pytest.raises(ConfigurationError):
            image.create_users(users_input, base_rootfs_path)

    @patch('rockcraft.oci._insert_into_image')
    def test_insert_content(self, mock_insert_into_img):
        image = oci.Image("a:b", Path("/c"))
        assert image.insert_content(Path('source'), Path('target')) is None
        mock_insert_into_img.assert_called_once_with(
            image.path / image.image_name, Path('source'), Path('target')
        )
        

@patch("subprocess.run")
def test__insert_into_image(mock_run):
    assert oci._insert_into_image(Path('image'), Path('source'), Path('target')) is None
    
    assert mock_run.mock_calls == [
        call(
            [
                "umoci",
                "insert",
                "--image",
                "image",
                "source",
                "target",
            ],
            capture_output=True,
            check=True,
            universal_newlines=True,
        )
    ]
