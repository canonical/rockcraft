# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2022 Canonical Ltd.
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

import argparse
from pathlib import Path
from unittest.mock import Mock, call

import pytest
from craft_cli import EmitterMode, emit
from craft_providers.bases.buildd import BuilddBaseAlias

from rockcraft import lifecycle


@pytest.fixture
def mock_project(mocker):
    _mock_project = mocker.patch("rockcraft.project")
    _mock_project.name = "test-name"
    _mock_project.platforms = {
        "test-platform": {
            "build_on": ["test-build-on"],
            "build_for": ["test-build-for"],
        }
    }
    yield _mock_project


@pytest.fixture()
def mock_provider(mocker, mock_instance, fake_provider):
    _mock_provider = Mock(wraps=fake_provider)
    mocker.patch(
        "rockcraft.lifecycle.providers.get_provider", return_value=_mock_provider
    )
    yield _mock_provider


@pytest.fixture()
def mock_get_instance_name(mocker):
    yield mocker.patch(
        "rockcraft.lifecycle.providers.get_instance_name",
        return_value="test-instance-name",
    )


@pytest.mark.parametrize(
    "command_name", ["pull", "overlay", "build", "stage", "prime", "pack"]
)
def test_run_run_in_provider(command_name, mocker, mock_project):
    """Verify `run()` calls `run_in_provider()` when not in managed or destructive
    mode.
    """
    mocker.patch("rockcraft.lifecycle.load_project", return_value=mock_project)
    mocker.patch("rockcraft.lifecycle.utils.is_managed_mode", return_value=False)
    mock_run_in_provider = mocker.patch("rockcraft.lifecycle.run_in_provider")
    lifecycle.run(command_name=command_name, parsed_args=argparse.Namespace())

    mock_run_in_provider.assert_called_once_with(
        mock_project, command_name, argparse.Namespace()
    )


def test_run_clean_provider(mocker, mock_project):
    """Verify `run()` calls `clean_provider()` when not in managed or destructive
    mode.
    """
    mocker.patch("rockcraft.lifecycle.load_project", return_value=mock_project)
    mocker.patch("rockcraft.lifecycle.utils.is_managed_mode", return_value=False)
    mock_clean_provider = mocker.patch("rockcraft.lifecycle.clean_provider")
    lifecycle.run(command_name="clean", parsed_args=argparse.Namespace())

    mock_clean_provider.assert_called_once_with(
        project_name="test-name", project_path=Path().absolute()
    )


def test_run_clean_part(mocker, mock_project, new_dir):
    """Verify cleaning a specific part."""
    mocker.patch("rockcraft.lifecycle.load_project", return_value=mock_project)
    mocker.patch("rockcraft.lifecycle.utils.is_managed_mode", return_value=True)
    mocker.patch(
        "rockcraft.lifecycle.utils.get_managed_environment_home_path",
        return_value=new_dir,
    )
    mocker.patch(
        "rockcraft.lifecycle.oci.Image.from_docker_registry",
        return_value=(Mock(), Mock()),
    )
    clean_mock = mocker.patch("rockcraft.parts.PartsLifecycle.clean")

    mock_project.parts = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle.run(command_name="clean", parsed_args=argparse.Namespace(parts=["foo"]))

    assert clean_mock.mock_calls == [call()]


def test_run_clean_destructive_mode(mocker, mock_project, new_dir):
    """Verify cleaning in destructive mode raises an error."""
    mocker.patch("rockcraft.lifecycle.load_project", return_value=mock_project)
    mocker.patch("rockcraft.lifecycle.utils.is_managed_mode", return_value=True)
    mocker.patch(
        "rockcraft.lifecycle.utils.get_managed_environment_home_path",
        return_value=new_dir,
    )
    mocker.patch(
        "rockcraft.lifecycle.oci.Image.from_docker_registry",
        return_value=(Mock(), Mock()),
    )
    clean_mock = mocker.patch("rockcraft.parts.PartsLifecycle.clean")

    mock_project.parts = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle.run(command_name="clean", parsed_args=argparse.Namespace(parts=["foo"]))

    assert clean_mock.mock_calls == [call()]


@pytest.mark.parametrize(
    "emit_mode,verbosity",
    [
        (EmitterMode.VERBOSE, ["--verbosity=verbose"]),
        (EmitterMode.QUIET, ["--verbosity=quiet"]),
        (EmitterMode.DEBUG, ["--verbosity=debug"]),
        (EmitterMode.TRACE, ["--verbosity=trace"]),
        (EmitterMode.BRIEF, ["--verbosity=brief"]),
    ],
)
@pytest.mark.parametrize(
    "rockcraft_base, provider_base",
    [
        ("ubuntu:18.04", BuilddBaseAlias.BIONIC),
        ("ubuntu:20.04", BuilddBaseAlias.FOCAL),
        ("ubuntu:22.04", BuilddBaseAlias.JAMMY),
    ],
)
def test_lifecycle_run_in_provider(
    mock_get_instance_name,
    mock_instance,
    mock_provider,
    mock_project,
    mocker,
    emit_mode,
    verbosity,
    rockcraft_base,
    provider_base,
):
    # mock provider calls
    mock_base_configuration = Mock()
    mock_get_base_configuration = mocker.patch(
        "rockcraft.lifecycle.providers.get_base_configuration",
        return_value=mock_base_configuration,
    )
    mock_capture_logs_from_instance = mocker.patch(
        "rockcraft.lifecycle.providers.capture_logs_from_instance"
    )
    mock_ensure_provider_is_available = mocker.patch(
        "rockcraft.lifecycle.providers.ensure_provider_is_available"
    )
    mock_project.build_base = rockcraft_base

    cwd = Path().absolute()

    # set emitter mode
    emit.set_mode(emit_mode)

    lifecycle.run_in_provider(
        project=mock_project,
        command_name="test",
        parsed_args=argparse.Namespace(),
    )

    mock_ensure_provider_is_available.assert_called_once_with(mock_provider)
    mock_get_instance_name.assert_called_once_with(
        project_name="test-name",
        project_path=cwd,
    )
    mock_get_base_configuration.assert_called_once_with(
        alias=provider_base,
        project_name="test-name",
        project_path=cwd,
    )
    mock_provider.launched_environment.assert_called_once_with(
        project_name="test-name",
        project_path=cwd,
        base_configuration=mock_base_configuration,
        build_base=provider_base.value,
        instance_name="test-instance-name",
    )
    mock_instance.mount.assert_called_once_with(
        host_source=cwd, target=Path("/root/project")
    )
    mock_instance.execute_run.assert_called_once_with(
        ["rockcraft", "test"] + verbosity,
        check=True,
        cwd=Path("/root/project"),
    )
    mock_capture_logs_from_instance.assert_called_once_with(mock_instance)


def test_clean_provider(emitter, mock_get_instance_name, mock_provider, tmpdir):
    lifecycle.clean_provider(project_name="test-project", project_path=tmpdir)

    mock_get_instance_name.assert_called_once_with(
        project_name="test-project", project_path=tmpdir
    )
    mock_provider.clean_project_environments.assert_called_once_with(
        instance_name="test-instance-name"
    )
    emitter.assert_interactions(
        [
            call("progress", "Cleaning build provider"),
            call("debug", "Cleaning instance test-instance-name"),
            call("progress", "Cleaned build provider", permanent=True),
        ]
    )
