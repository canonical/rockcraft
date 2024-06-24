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
from pathlib import Path
import textwrap
from unittest.mock import DEFAULT, call

import pytest
import yaml
from craft_cli import emit
from rockcraft import cli, extensions, services
from rockcraft.application import Rockcraft
from rockcraft.models import project


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


@pytest.mark.usefixtures("new_dir")
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


@pytest.mark.usefixtures("new_dir")
def test_run_init_with_name(mocker):
    mocker.patch.object(sys, "argv", ["rockcraft", "init", "--name=foobar"])

    cli.run()

    rockcraft_yaml_path = Path("rockcraft.yaml")
    rock_project = project.Project.unmarshal(
        yaml.safe_load(rockcraft_yaml_path.read_text())
    )

    assert rock_project.name == "foobar"


@pytest.mark.usefixtures("new_dir")
def test_run_init_with_invalid_name(mocker):
    mocker.patch.object(sys, "argv", ["rockcraft", "init", "--name=f"])
    return_code = cli.run()
    assert return_code == 1


@pytest.mark.usefixtures("new_dir")
def test_run_init_fallback_name(mocker):
    mocker.patch.object(sys, "argv", ["rockcraft", "init"])
    mocker.patch("pathlib.Path.cwd", return_value=pathlib.Path("/f"))

    cli.run()

    rockcraft_yaml_path = Path("rockcraft.yaml")
    rock_project = project.Project.unmarshal(
        yaml.safe_load(rockcraft_yaml_path.read_text())
    )

    assert rock_project.name == "my-rock-name"


def test_run_init_flask(mocker, emitter, monkeypatch, new_dir, tmp_path):
    (new_dir / "requirements.txt").write_text("Flask", encoding="utf-8")
    (new_dir / "app.py").write_text("app = object()", encoding="utf-8")

    mocker.patch.object(
        sys,
        "argv",
        ["rockcraft", "init", "--profile=flask-framework", "--name", "test-name"],
    )

    cli.run()

    rockcraft_yaml_path = Path("rockcraft.yaml")
    rock_project_yaml = yaml.safe_load(rockcraft_yaml_path.read_text())

    assert len(rock_project_yaml["summary"]) < 80
    assert len(rock_project_yaml["description"].split()) < 100
    assert rockcraft_yaml_path.read_text() == textwrap.dedent(
        """\
            name: test-name
            # see https://documentation.ubuntu.com/rockcraft/en/stable/explanation/bases/
            # for more information about bases and using 'bare' bases for chiselled rocks
            base: ubuntu@22.04 # the base environment for this Flask application
            version: '0.1' # just for humans. Semantic versioning is recommended
            summary: A summary of your Flask application # 79 char long summary
            description: |
                This is test-name's description. You have a paragraph or two to tell the
                most important story about it. Keep it under 100 words though,
                we live in tweetspace and your description wants to look good in the
                container registries out there.
            platforms: # the platforms this rock should be built on and run on
                amd64:

            # to ensure the flask-framework extension works properly, your Flask application
            # should have an `app.py` file with an `app` object as the WSGI entrypoint.
            # a `requirements.txt` file with at least the flask package should also exist.
            # see https://documentation.ubuntu.com/rockcraft/en/stable/reference/extensions/flask-framework
            # for more information.
            extensions:
                - flask-framework

            # uncomment the sections you need and adjust according to your requirements.
            # parts:  # you need to uncomment this line to add or update any part.

            #   flask-framework/install-app:
            #     prime:
            #       # by default, only the files in app/, templates/, static/, migrate,
            #       # migrate.sh and app.py are copied into the image. You can modify the list
            #       # below to override the default list and include or exclude specific
            #       # files/directories in your project.
            #       # note: prefix each entry with "flask/app/" followed by the local path.
            #       - flask/app/.env
            #       - flask/app/app.py
            #       - flask/app/webapp
            #       - flask/app/templates
            #       - flask/app/static
            #       # you may need packages to build a python package. Add them here if necessary.
            #       build-packages:
            #           # for example, if you need pkg-config and libxmlsec1-dev to build one
            #           # of your packages:
            #           - pkg-config
            #           - libxmlsec1-dev

            # you can add package slices or Debian packages to the image.
            # package slices are subsets of Debian packages, which result
            # in smaller and more secure images.
            # see https://documentation.ubuntu.com/rockcraft/en/latest/explanation/chisel/

            # add this part if you want to add packages slices to your image.
            # you can find a list of packages slices at https://github.com/canonical/chisel-releases
            #   flask-framework/runtime-slices:
            #     plugin: nil
            #     stage-packages:
            #     # list the required package slices for your flask application below.
            #     # for example, for the slice libs of libpq5:
            #     - libpq5_libs

            # if you want to add a Debian package to your image, add the next part
            #   flask-framework/runtime-debs:
            #     plugin: nil
            #     stage-packages:
            #     # list required Debian packages for your flask application below.
            #     - libpq5
        """
    )
    emitter.assert_message(
        textwrap.dedent(
            """\
        Created 'rockcraft.yaml'.
        Go to https://documentation.ubuntu.com/rockcraft/en/stable/reference/extensions/flask-framework to read more about the 'flask-framework' profile."""
        )
    )
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "0")
    project.Project.unmarshal(extensions.apply_extensions(tmp_path, rock_project_yaml))
