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

import pytest
from craft_parts import Action, PartsError, Step

import tests
from rockcraft import parts
from rockcraft.errors import RockcraftError


@tests.linux_only
def test_parts_lifecycle_prime_dir(new_dir):
    parts_data = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle = parts.PartsLifecycle(
        all_parts=parts_data,
        work_dir=Path("/some/workdir"),
        part_names=None,
        base_layer_dir=new_dir,
        base_layer_hash=b"digest",
    )
    assert lifecycle.prime_dir == Path("/some/workdir/prime")


@tests.linux_only
def test_parts_lifecycle_run(new_dir):
    parts_data = {
        "foo": {
            "plugin": "dump",
            "source": "dir1",
        }
    }

    Path("dir1").mkdir()
    Path("dir1/foo.txt").touch()

    lifecycle = parts.PartsLifecycle(
        all_parts=parts_data,
        work_dir=Path("."),
        part_names=None,
        base_layer_dir=new_dir,
        base_layer_hash=b"digest",
    )
    lifecycle.run("prime")

    assert Path(lifecycle.prime_dir, "foo.txt").is_file()


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
def test_parts_lifecycle_run_shell(new_dir, mocker, step_name, expected_last_step):
    """Check if the last step executed before shell is the previous step."""
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

    lifecycle = parts.PartsLifecycle(
        all_parts=parts_data,
        work_dir=Path("."),
        part_names=None,
        base_layer_dir=new_dir,
        base_layer_hash=b"digest",
    )
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
    new_dir, mocker, step_name, expected_last_step
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

    lifecycle = parts.PartsLifecycle(
        all_parts=parts_data,
        work_dir=Path("."),
        part_names=None,
        base_layer_dir=new_dir,
        base_layer_hash=b"digest",
    )
    lifecycle.run(step_name, shell_after=True)

    assert last_step == expected_last_step
    assert shell_mock.mock_calls == [call(["bash"], check=False, cwd=None)]


def assert_errors_match(
    rockcraft_error: RockcraftError, parts_error: PartsError
) -> None:
    """Assert that the RockcraftError's fields match those on the PartsError."""
    assert str(rockcraft_error) == parts_error.brief
    assert rockcraft_error.details == parts_error.details
    assert rockcraft_error.resolution == parts_error.resolution


@tests.linux_only
def test_parts_lifecycle_init_error(new_dir):
    parts_data = {
        "foo": {
            "invalid": True,
        }
    }

    with pytest.raises(parts.PartsLifecycleError) as exc:
        parts.PartsLifecycle(
            all_parts=parts_data,
            work_dir=Path("."),
            part_names=None,
            base_layer_dir=new_dir,
            base_layer_hash=b"digest",
        )

    rockcraft_error = exc.value
    parts_error = cast(PartsError, rockcraft_error.__cause__)

    assert_errors_match(rockcraft_error, parts_error)


@tests.linux_only
def test_parts_lifecycle_run_error(new_dir, mocker):
    parts_data = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle = parts.PartsLifecycle(
        all_parts=parts_data,
        work_dir=Path("."),
        part_names=["fake_part"],
        base_layer_dir=new_dir,
        base_layer_hash=b"digest",
    )

    with pytest.raises(parts.PartsLifecycleError) as exc:
        # This fails because `part_names` references a part that doesn't exist
        lifecycle.run(step_name="pull")

    rockcraft_error = exc.value
    parts_error = cast(PartsError, rockcraft_error.__cause__)

    assert_errors_match(rockcraft_error, parts_error)


@tests.linux_only
def test_parts_lifecycle_clean(new_dir, emitter):
    parts_data = {
        "foo": {
            "plugin": "nil",
        }
    }

    lifecycle = parts.PartsLifecycle(
        parts_data,
        work_dir=new_dir,
        part_names=None,
        base_layer_dir=new_dir,
        base_layer_hash=b"digest",
    )
    lifecycle.clean()
    emitter.assert_progress("Cleaning all parts")


@tests.linux_only
def test_parts_lifecycle_clean_parts(new_dir, emitter):
    parts_data = {
        "foo": {
            "plugin": "nil",
        },
        "bar": {
            "plugin": "nil",
        },
    }

    lifecycle = parts.PartsLifecycle(
        parts_data,
        work_dir=new_dir,
        part_names=["foo"],
        base_layer_dir=new_dir,
        base_layer_hash=b"digest",
    )
    lifecycle.clean()
    emitter.assert_progress("Cleaning parts: foo")
