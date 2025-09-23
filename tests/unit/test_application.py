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
from textwrap import dedent

import pytest
from rockcraft import cli, plugins


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
