# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2021-2022 Canonical Ltd
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

import os

import pytest
import xdg  # type: ignore


@pytest.fixture
def new_dir(tmpdir):
    """Change to a new temporary directory."""

    cwd = os.getcwd()
    os.chdir(tmpdir)

    yield tmpdir

    os.chdir(cwd)


@pytest.fixture(autouse=True)
def temp_xdg(tmpdir, mocker):
    """Use a temporary location for XDG directories."""

    mocker.patch(
        "xdg.BaseDirectory.xdg_config_home", new=os.path.join(tmpdir, ".config")
    )
    mocker.patch("xdg.BaseDirectory.xdg_data_home", new=os.path.join(tmpdir, ".local"))
    mocker.patch("xdg.BaseDirectory.xdg_cache_home", new=os.path.join(tmpdir, ".cache"))
    mocker.patch(
        "xdg.BaseDirectory.xdg_config_dirs",
        new=[xdg.BaseDirectory.xdg_config_home],  # pyright: ignore
    )
    mocker.patch(
        "xdg.BaseDirectory.xdg_data_dirs",
        new=[xdg.BaseDirectory.xdg_data_home],  # pyright: ignore
    )
    mocker.patch.dict(os.environ, {"XDG_CONFIG_HOME": os.path.join(tmpdir, ".config")})


@pytest.fixture()
def reset_callbacks():
    """Fixture that resets the status of craft-part's various lifecycle callbacks,
    so that tests can start with a clean slate.
    """
    # pylint: disable=import-outside-toplevel

    from craft_parts import callbacks

    callbacks.unregister_all()
    yield
    callbacks.unregister_all()


class RecordingEmitter:
    """Record what is shown using the emitter and provide a nice API for tests."""

    def __init__(self):
        self.progress = []
        self.message = []
        self.trace = []
        self.emitted = []
        self.raw = []

    def record(self, level, text):
        """Record the text for the specific level and in the general storages."""
        getattr(self, level).append(text)
        self.emitted.append(text)
        self.raw.append((level, text))

    def _check(self, expected, storage):
        """Really verify messages."""
        for pos, recorded_msg in enumerate(storage):
            if recorded_msg == expected[0]:
                break
        else:
            raise AssertionError(f"Initial test message not found in {storage}")

        recorded = storage[pos : pos + len(expected)]  # pylint: disable=W0631
        assert recorded == expected

    def assert_recorded(self, expected):
        """Verify that the given messages were recorded consecutively."""
        self._check(expected, self.emitted)

    def assert_recorded_raw(self, expected):
        """Verify that the given messages (with specific level) were recorded consecutively."""
        self._check(expected, self.raw)
