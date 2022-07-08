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

import pytest

import tests
from rockcraft import parts


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
        base="ubuntu:20.04",
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
        base="ubuntu:20.04",
        base_layer_dir=new_dir,
        base_layer_hash=b"digest",
    )
    lifecycle.run(parts.Step.PRIME)

    assert Path(lifecycle.prime_dir, "foo.txt").is_file()


@tests.linux_only
def test_parts_lifecycle_error(new_dir):
    parts_data = {
        "foo": {
            "invalid": True,
        }
    }

    with pytest.raises(parts.PartsLifecycleError):
        parts.PartsLifecycle(
            all_parts=parts_data,
            work_dir=Path("."),
            base="ubuntu:20.04",
            base_layer_dir=new_dir,
            base_layer_hash=b"digest",
        )
