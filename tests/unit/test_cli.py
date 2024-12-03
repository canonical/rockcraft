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
import pathlib
import sys
import textwrap
from distutils.dir_util import copy_tree
from pathlib import Path
from unittest.mock import DEFAULT, call

import pytest
import yaml
from craft_cli import emit
from rockcraft import cli, extensions, services
from rockcraft.application import APP_METADATA, Rockcraft
from rockcraft.models import project

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"


def test_run_pack_services(mocker, monkeypatch, tmp_path):
    # Pretend it's running inside the managed instance
    monkeypatch.setenv("CRAFT_MANAGED_MODE", "1")

    log_path = tmp_path / "rockcraft.log"
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(Rockcraft, "get_project")
    mocker.patch.object(Rockcraft, "log_path", new=log_path)

    fake_prime_dir = Path("/fake/prime/dir")

    # Mock the relevant methods from the lifecycle and package services
    lifecycle_mocks = mocker.patch.multiple(
        services.RockcraftLifecycleService,
        setup=DEFAULT,
        prime_dir=fake_prime_dir,
        run=DEFAULT,
        project_info=DEFAULT,
    )

    package_mocks = mocker.patch.multiple(
        services.RockcraftPackageService, write_metadata=DEFAULT, pack=DEFAULT
    )

    command_line = ["rockcraft", "pack"]
    mocker.patch.object(sys, "argv", command_line)

    cli.run()

    lifecycle_mocks["run"].assert_called_once_with(step_name="prime")

    package_mocks["write_metadata"].assert_called_once_with(fake_prime_dir)
    package_mocks["pack"].assert_called_once_with(fake_prime_dir, Path())

    assert mock_ended_ok.called
    assert log_path.is_file()


@pytest.fixture
def valid_dir(new_dir, monkeypatch):
    valid = pathlib.Path(new_dir) / "valid"
    valid.mkdir()
    monkeypatch.chdir(valid)


@pytest.mark.usefixtures("valid_dir")
def test_run_init(mocker):
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", "init"])

    cli.run()

    rockcraft_yaml_path = Path("rockcraft.yaml")
    rock_project = project.Project.unmarshal(
        yaml.safe_load(rockcraft_yaml_path.read_text())
    )

    assert len(rock_project.summary) < 80
    assert len(rock_project.description.split()) < 100
    assert mock_ended_ok.mock_calls == [call()]
    assert rock_project.base == "ubuntu@24.04"


@pytest.mark.usefixtures("valid_dir")
def test_run_init_with_name(mocker):
    mocker.patch.object(sys, "argv", ["rockcraft", "init", "--name=foobar"])

    cli.run()

    rockcraft_yaml_path = Path("rockcraft.yaml")
    rock_project = project.Project.unmarshal(
        yaml.safe_load(rockcraft_yaml_path.read_text())
    )

    assert rock_project.name == "foobar"


@pytest.mark.usefixtures("valid_dir")
def test_run_init_with_invalid_name(mocker):
    mocker.patch.object(sys, "argv", ["rockcraft", "init", "--name=f"])
    return_code = cli.run()
    assert return_code == 1


def test_run_init_fallback_name(mocker, new_dir, monkeypatch):
    mocker.patch.object(sys, "argv", ["rockcraft", "init"])
    invalid_dir = pathlib.Path(new_dir) / "f"
    invalid_dir.mkdir()
    monkeypatch.chdir(invalid_dir)

    cli.run()

    rockcraft_yaml_path = invalid_dir / "rockcraft.yaml"
    rock_project = project.Project.unmarshal(
        yaml.safe_load(rockcraft_yaml_path.read_text())
    )

    assert rock_project.name == "my-rock-name"


def test_run_init_flask(mocker, emitter, monkeypatch, new_dir, tmp_path):
    copy_tree(Path(f"{DATA_DIR}/flask"), tmp_path)

    mocker.patch.object(
        sys,
        "argv",
        ["rockcraft", "init", "--profile=flask-framework", "--name", "test-name"],
    )

    cli.run()

    versioned_url = APP_METADATA.versioned_docs_url

    rockcraft_yaml_path = Path("rockcraft.yaml")
    rock_project_yaml = yaml.safe_load(rockcraft_yaml_path.read_text())

    assert len(rock_project_yaml["summary"]) < 80
    assert len(rock_project_yaml["description"].split()) < 100
    expected_rockcraft_yaml_path = Path(tmp_path / "expected_rockcraft.yaml")
    assert rockcraft_yaml_path.read_text() == expected_rockcraft_yaml_path.read_text()

    emitter.assert_message(
        textwrap.dedent(
            f"""\
        Go to {versioned_url}/reference/extensions/flask-framework to read more about the 'flask-framework' profile."""
        )
    )
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "0")
    project.Project.unmarshal(extensions.apply_extensions(tmp_path, rock_project_yaml))


def test_run_init_flask_async(mocker, emitter, monkeypatch, new_dir, tmp_path):
    copy_tree(Path(f"{DATA_DIR}/flask"), tmp_path)

    mocker.patch.object(
        sys,
        "argv",
        ["rockcraft", "init", "--profile=flask-framework", "--name", "test-name"],
    )
    cli.run()
    rockcraft_yaml_path = Path("rockcraft_async.yaml")
    rock_project_yaml = yaml.safe_load(rockcraft_yaml_path.read_text())

    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "0")
    project.Project.unmarshal(extensions.apply_extensions(tmp_path, rock_project_yaml))

    emitter.assert_message("Successfully initialised project.")


def test_run_init_django(mocker, emitter, monkeypatch, new_dir, tmp_path):
    copy_tree(Path(f"{DATA_DIR}/django"), tmp_path)

    mocker.patch.object(
        sys,
        "argv",
        ["rockcraft", "init", "--profile=django-framework", "--name", "test-name"],
    )

    cli.run()

    versioned_url = APP_METADATA.versioned_docs_url

    rockcraft_yaml_path = Path(tmp_path / "rockcraft.yaml")
    expected_rockcraft_yaml_path = Path(tmp_path / "expected_rockcraft.yaml")
    rock_project_yaml = yaml.safe_load(rockcraft_yaml_path.read_text())

    assert len(rock_project_yaml["summary"]) < 80
    assert len(rock_project_yaml["description"].split()) < 100
    assert rockcraft_yaml_path.read_text() == expected_rockcraft_yaml_path.read_text()

    emitter.assert_message(
        textwrap.dedent(
            f"""\
        Go to {versioned_url}/reference/extensions/django-framework to read more about the 'django-framework' profile."""
        )
    )
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "0")
    project.Project.unmarshal(extensions.apply_extensions(tmp_path, rock_project_yaml))


def test_run_init_django_async(mocker, emitter, monkeypatch, new_dir, tmp_path):
    copy_tree(Path(f"{DATA_DIR}/django"), tmp_path)

    mocker.patch.object(
        sys,
        "argv",
        ["rockcraft", "init", "--profile=django-framework", "--name", "test-name"],
    )
    cli.run()
    rockcraft_yaml_path = Path("rockcraft_async.yaml")
    rock_project_yaml = yaml.safe_load(rockcraft_yaml_path.read_text())

    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "0")
    project.Project.unmarshal(extensions.apply_extensions(tmp_path, rock_project_yaml))

    emitter.assert_message("Successfully initialised project.")
