# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2025 Canonical Ltd.
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
import dataclasses
from textwrap import dedent

import pytest
import rockcraft
from rockcraft import cli, plugins
from rockcraft.application import APP_METADATA

pytestmark = [pytest.mark.usefixtures("enable_overlay_feature")]


@pytest.mark.parametrize("build_base", ["ubuntu@20.04", "ubuntu@24.04", "ubuntu@25.10"])
def test_get_app_plugins_build_base(tmp_path, monkeypatch, mocker, build_base):
    monkeypatch.chdir(tmp_path)
    project = tmp_path / "rockcraft.yaml"
    project.write_text(
        dedent(f"""\
    name: my-project
    build-base: {build_base}
    """)
    )
    app = cli._create_app()
    spied_get_plugins = mocker.spy(plugins, "get_plugins")
    app._configure_early_services()
    _ = app._get_app_plugins()
    spied_get_plugins.assert_called_once_with(build_base)


@pytest.mark.parametrize("base", ["ubuntu@20.04", "ubuntu@24.04", "ubuntu@25.10"])
def test_get_app_plugins_base(tmp_path, monkeypatch, mocker, base):
    monkeypatch.chdir(tmp_path)
    project = tmp_path / "rockcraft.yaml"
    project.write_text(
        dedent(f"""\
    name: my-project
    base: {base}
    """)
    )
    app = cli._create_app()
    spied_get_plugins = mocker.spy(plugins, "get_plugins")
    app._configure_early_services()
    _ = app._get_app_plugins()
    spied_get_plugins.assert_called_once_with(base)


def test_get_app_plugins_missing_base(tmp_path, monkeypatch, mocker):
    monkeypatch.chdir(tmp_path)
    project = tmp_path / "rockcraft.yaml"
    project.write_text("name: my-project")
    app = cli._create_app()
    spied_get_plugins = mocker.spy(plugins, "get_plugins")
    app._configure_early_services()
    _ = app._get_app_plugins()
    spied_get_plugins.assert_called_once_with(None)


def test_get_app_plugins_missing_project(tmp_path, monkeypatch, mocker):
    monkeypatch.chdir(tmp_path)
    app = cli._create_app()
    spied_get_plugins = mocker.spy(plugins, "get_plugins")
    app._configure_early_services()
    _ = app._get_app_plugins()
    spied_get_plugins.assert_called_once_with(None)


@pytest.mark.parametrize(
    ("version", "expected_url"),
    [
        ("1.20.0", "https://documentation.ubuntu.com/rockcraft/1"),
        ("2.0.1", "https://documentation.ubuntu.com/rockcraft/2"),
    ],
)
def test_docs_url_uses_major_version(monkeypatch, version, expected_url):
    """Released docs URLs point at the major version only.

    Regression test for #1312. The expected URL is spelled out in full on
    purpose: deriving it from the property under test would track any change to
    the URL scheme instead of catching it.
    """
    # AppMetadata is a frozen dataclass whose 'version' field is init=False and
    # derived in __post_init__ from the app package's __version__. replace()
    # re-runs that derivation, so the real APP_METADATA is left alone.
    monkeypatch.setattr(rockcraft, "__version__", version)
    app_metadata = dataclasses.replace(APP_METADATA)

    assert app_metadata.versioned_docs_url == expected_url
