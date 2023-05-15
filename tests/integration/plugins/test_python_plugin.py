# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import typing
from dataclasses import dataclass
from pathlib import Path

import pytest
from craft_parts import callbacks
from craft_parts.utils.os_utils import OsRelease

from rockcraft import plugins
from rockcraft.parts import PartsLifecycle
from rockcraft.project import Project
from tests.util import ubuntu_only

pytestmark = ubuntu_only

# Extract the possible "base" values from the Literal annotation.
ALL_BASES = typing.get_args(typing.get_type_hints(Project)["base"])

BARE_BASES = {"bare"}
UBUNTU_BASES = set(ALL_BASES) - BARE_BASES


@pytest.fixture(autouse=True)
def setup_python_test(monkeypatch):
    # Keep craft-parts from trying to refresh apt's cache, so that we can run
    # this test as regular users.
    monkeypatch.setenv("CRAFT_PARTS_PACKAGE_REFRESH", "0")
    plugins.register()


def run_lifecycle(base: str, work_dir: Path) -> None:
    source = Path(__file__).parent / "python_source"

    parts = {
        "my-part": {
            "plugin": "python",
            "source": str(source),
            "stage-packages": ["python3-venv"],
        }
    }

    callbacks.unregister_all()
    lifecycle = PartsLifecycle(
        all_parts=parts,
        work_dir=work_dir,
        part_names=None,
        base_layer_dir=Path("unused"),
        base_layer_hash=b"deadbeef",
        base=base,
    )

    lifecycle.run("stage")
    callbacks.unregister_all()


@pytest.mark.parametrize("base", tuple(UBUNTU_BASES))
def test_python_plugin_ubuntu(base, tmp_path):

    work_dir = tmp_path / "work"

    run_lifecycle(base, work_dir)

    bin_dir = work_dir / "stage/bin"

    # Ubuntu base: the Python symlinks in bin/ must *not* exist, because of the
    # usrmerge handling
    assert list(bin_dir.glob("python*")) == []

    # Check the shebang in the "hello" script
    expected_shebang = "#!/bin/python3"
    hello = bin_dir / "hello"
    assert hello.read_text().startswith(expected_shebang)


@dataclass
class ExpectedValues:
    """Expected venv Python symlinks and the "actual" Python target."""

    symlinks: typing.List[str]
    symlink_target: str


# A mapping from host Ubuntu to expected Python symlinks; We need this mapping
# because the "bare" test runs on the host machine as the "build base".
RELEASE_TO_VALUES = {
    "22.04": ExpectedValues(
        symlinks=["python", "python3", "python3.10"],
        symlink_target="../usr/bin/python3.10",
    ),
    "20.04": ExpectedValues(
        symlinks=["python", "python3"], symlink_target="../usr/bin/python3.8"
    ),
}


def test_python_plugin_bare(tmp_path):
    work_dir = tmp_path / "work"

    run_lifecycle("bare", work_dir)

    bin_dir = work_dir / "stage/bin"

    release = OsRelease().version_id()
    expected_values = RELEASE_TO_VALUES[release]

    # Bare base: the Python symlinks in bin/ *must* exist, and "python3" must
    # point to the "concrete" part-provided python binary
    assert sorted(bin_dir.glob("python*")) == [
        bin_dir / i for i in expected_values.symlinks
    ]
    # (Python 3.8 does not have Path.readlink())
    assert os.readlink(bin_dir / "python3") == expected_values.symlink_target

    # Check the shebang in the "hello" script
    expected_shebang = "#!/bin/python3"
    hello = bin_dir / "hello"
    assert hello.read_text().startswith(expected_shebang)
