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

from pathlib import Path
from typing import cast
from unittest.mock import call

import craft_cli
import pytest
from craft_parts import Action, PartsError, Step, callbacks

import tests
from rockcraft import parts
from rockcraft.errors import PartsLifecycleError, RockcraftError


@pytest.fixture
def parts_data():
    yield {
        "foo": {
            "plugin": "nil",
        }
    }


@pytest.fixture
def create_lifecycle(new_dir):
    def _inner_create(**kwargs) -> parts.PartsLifecycle:
        kwargs.setdefault("base_layer_hash", b"digest")
        kwargs.setdefault("base", "unused")
        kwargs.setdefault("project_name", "my-project")
        kwargs.setdefault("part_names", None)
        kwargs.setdefault("base_layer_dir", new_dir)
        kwargs.setdefault("work_dir", new_dir)

        return parts.PartsLifecycle(
            **kwargs,
        )

    return _inner_create


@tests.linux_only
def test_parts_lifecycle_prime_dir(create_lifecycle):
    parts_data = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle = create_lifecycle(all_parts=parts_data, work_dir=Path("/some/workdir"))
    assert lifecycle.prime_dir == Path("/some/workdir/prime")


@tests.linux_only
def test_parts_lifecycle_project_info(create_lifecycle):
    parts_data = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle = create_lifecycle(all_parts=parts_data, work_dir=Path("/some/workdir"))
    assert lifecycle.project_info.work_dir == Path("/some/workdir")
    assert lifecycle.project_info.base == "unused"


@tests.linux_only
def test_parts_lifecycle_run(create_lifecycle):
    parts_data = {
        "foo": {
            "plugin": "dump",
            "source": "dir1",
        }
    }

    Path("dir1").mkdir()
    Path("dir1/foo.txt").touch()

    lifecycle = create_lifecycle(all_parts=parts_data, work_dir=Path("."))
    lifecycle.run("prime")

    assert Path(lifecycle.prime_dir, "foo.txt").is_file()


@pytest.mark.parametrize("repos", [[{"type": "apt", "ppa": "mozillateam/ppa"}]])
@tests.linux_only
def test_run_installs_package_repositories(
    mocker, parts_data, tmp_path, repos, create_lifecycle
):
    lifecycle = create_lifecycle(
        all_parts=parts_data,
        work_dir=tmp_path,
        base_layer_dir=tmp_path,
        package_repositories=repos,
    )
    lcm = mocker.patch.object(lifecycle, "_lcm")
    lcm.plan.return_value = []
    mocker.patch("craft_archives.repo.install", return_value=False)
    progress_spy = mocker.spy(craft_cli.emit, "progress")

    lifecycle.run("pull")

    progress_spy.assert_has_calls(
        [
            call("Installing package repositories"),
            call("Package repositories installed", permanent=True),
        ]
    )


@pytest.mark.parametrize(
    "step_name,expected_last_step",
    [
        ("pull", None),
        ("overlay", Step.PULL),
        ("build", Step.OVERLAY),
        ("stage", Step.BUILD),
        ("prime", Step.STAGE),
    ],
)
@tests.linux_only
def test_parts_lifecycle_run_shell(
    mocker, step_name, expected_last_step, parts_data, create_lifecycle
):
    """Check if the last step executed before shell is the previous step."""
    last_step = None

    def _fake_execute(_, action: Action, **kwargs):  # pylint: disable=unused-argument
        nonlocal last_step
        last_step = action.step

    mocker.patch("craft_parts.executor.Executor.execute", new=_fake_execute)
    shell_mock = mocker.patch("subprocess.run")

    lifecycle = create_lifecycle(all_parts=parts_data, work_dir=Path("."))
    lifecycle.run(step_name, shell=True)

    assert last_step == expected_last_step
    assert shell_mock.mock_calls == [call(["bash"], check=False, cwd=None)]


@pytest.mark.parametrize(
    "step_name,expected_last_step",
    [
        ("pull", Step.PULL),
        ("overlay", Step.OVERLAY),
        ("build", Step.BUILD),
        ("stage", Step.STAGE),
        ("prime", Step.PRIME),
    ],
)
@tests.linux_only
def test_parts_lifecycle_run_shell_after(
    mocker, step_name, expected_last_step, create_lifecycle
):
    """Check if the last step executed before shell is the current step."""
    last_step = None

    def _fake_execute(_, action: Action, **kwargs):  # pylint: disable=unused-argument
        nonlocal last_step
        last_step = action.step

    mocker.patch("craft_parts.executor.Executor.execute", new=_fake_execute)
    shell_mock = mocker.patch("subprocess.run")

    parts_data = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle = create_lifecycle(all_parts=parts_data, work_dir=Path("."))
    lifecycle.run(step_name, shell_after=True)

    assert last_step == expected_last_step
    assert shell_mock.mock_calls == [call(["bash"], check=False, cwd=None)]


@pytest.mark.parametrize(
    "internal_exception,expected_exception_type",
    [
        (PartsError("Unexpected error"), PartsLifecycleError),
        (RuntimeError("Unexpected error"), RuntimeError),
        (FileNotFoundError(2, "Unexpected error"), PartsLifecycleError),
        (Exception("Unexpected error"), PartsLifecycleError),
    ],
)
@tests.linux_only
def test_parts_lifecycle_run_debug(
    mocker, internal_exception, expected_exception_type, create_lifecycle
):
    """Check that when "debug" is True, a shell is launched when an error is raised."""

    mocker.patch(
        "craft_parts.executor.Executor.execute",
        side_effect=internal_exception,
    )
    shell_mock = mocker.patch("rockcraft.parts.launch_shell")

    parts_data = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle = create_lifecycle(all_parts=parts_data, work_dir=Path("."))
    with pytest.raises(expected_exception_type, match="Unexpected error"):
        lifecycle.run("prime", debug=True)

    shell_mock.assert_called_once_with()


def assert_errors_match(
    rockcraft_error: RockcraftError, parts_error: PartsError
) -> None:
    """Assert that the RockcraftError's fields match those on the PartsError."""
    assert str(rockcraft_error) == parts_error.brief
    assert rockcraft_error.details == parts_error.details
    assert rockcraft_error.resolution == parts_error.resolution


@tests.linux_only
def test_parts_lifecycle_init_error(create_lifecycle):
    parts_data = {
        "foo": {
            "invalid": True,
        }
    }

    with pytest.raises(parts.PartsLifecycleError) as exc:
        create_lifecycle(all_parts=parts_data, work_dir=Path("."))

    rockcraft_error = exc.value
    parts_error = cast(PartsError, rockcraft_error.__cause__)

    assert_errors_match(rockcraft_error, parts_error)


@tests.linux_only
def test_parts_lifecycle_run_error(create_lifecycle):
    parts_data = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle = create_lifecycle(
        all_parts=parts_data, work_dir=Path("."), part_names=["fake_part"]
    )

    with pytest.raises(parts.PartsLifecycleError) as exc:
        # This fails because `part_names` references a part that doesn't exist
        lifecycle.run(step_name="pull")

    rockcraft_error = exc.value
    parts_error = cast(PartsError, rockcraft_error.__cause__)

    assert_errors_match(rockcraft_error, parts_error)


@tests.linux_only
def test_parts_lifecycle_clean(create_lifecycle, emitter):
    parts_data = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle = create_lifecycle(all_parts=parts_data, work_dir=Path("."))
    lifecycle.clean()
    emitter.assert_progress("Cleaning all parts")


@tests.linux_only
def test_parts_lifecycle_clean_parts(create_lifecycle, emitter):
    parts_data = {
        "foo": {
            "plugin": "nil",
        },
        "bar": {
            "plugin": "nil",
        },
    }

    lifecycle = create_lifecycle(all_parts=parts_data, part_names=["foo"])
    lifecycle.clean()
    emitter.assert_progress("Cleaning parts: foo")


@tests.linux_only
def test_parts_register_overlay_callback(mocker, create_lifecycle):
    """Test that PartsLifecycle registers the overlay callback."""
    # pylint: disable=protected-access
    register_spy = mocker.spy(callbacks, "register_configure_overlay")

    # Check that creating the lifecycle registers the callback
    assert not register_spy.called
    create_lifecycle(all_parts={})
    register_spy.assert_called_once_with(parts._install_overlay_repositories)

    # Check that creating another lifecycle does *not* raise an error from re-
    # registering the callback.
    create_lifecycle(all_parts={})
