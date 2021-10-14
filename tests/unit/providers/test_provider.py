# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021 Canonical Ltd.
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

import pytest

from rockcraft import providers


def test_get_command_environment_minimal(monkeypatch):
    monkeypatch.setenv("IGNORE_ME", "or-im-failing")
    monkeypatch.setenv("PATH", "not-using-host-path")
    provider = providers.LXDProvider()

    env = provider.get_command_environment()

    assert env == {
        "ROCKCRAFT_MANAGED_MODE": "1",
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
    }


def test_get_command_environment_all_opts(monkeypatch):
    monkeypatch.setenv("IGNORE_ME", "or-im-failing")
    monkeypatch.setenv("PATH", "not-using-host-path")
    monkeypatch.setenv("http_proxy", "test-http-proxy")
    monkeypatch.setenv("https_proxy", "test-https-proxy")
    monkeypatch.setenv("no_proxy", "test-no-proxy")
    provider = providers.LXDProvider()

    env = provider.get_command_environment()

    assert env == {
        "ROCKCRAFT_MANAGED_MODE": "1",
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
        "http_proxy": "test-http-proxy",
        "https_proxy": "test-https-proxy",
        "no_proxy": "test-no-proxy",
    }


def test_get_instance_name(mock_path):
    provider = providers.LXDProvider()

    assert (
        provider.get_instance_name(
            project_name="my-project-name",
            project_path=mock_path,
        )
        == "rockcraft-my-project-name-445566"
    )


@pytest.mark.parametrize(
    "name,expected_valid,expected_reason",
    [
        ("ubuntu:18.04", True, None),
        ("ubuntu:20.04", True, None),
        (
            "ubuntu:19.04",
            False,
            "Base 'ubuntu:19.04' is not supported (must be 'ubuntu:18.04' or 'ubuntu:20.04')",
        ),
    ],
)
def test_is_base_available(name, expected_valid, expected_reason):
    provider = providers.LXDProvider()

    valid, reason = provider.is_base_available(name)

    assert (valid, reason) == (expected_valid, expected_reason)
