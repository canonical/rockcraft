#!/usr/bin/env python3
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2021 Canonical Ltd
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

from unittest.mock import call, patch

import pytest
from craft_cli.errors import CraftError

from rockcraft.cli import run


@pytest.fixture
def ui_init_mock():
    """Mock for ui.init."""
    patcher = patch("rockcraft.ui.init")
    yield patcher.start()
    patcher.stop()


@pytest.fixture
def lifecycle_pack_mock():
    """Mock for ui.init."""
    patcher = patch("rockcraft.lifecycle.pack")
    yield patcher.start()
    patcher.stop()


def test_run_defaults(emit_mock, ui_init_mock, lifecycle_pack_mock):
    run(["rockcraft", "pack"])

    assert ui_init_mock.mock_calls == [call(["rockcraft", "pack"])]
    assert lifecycle_pack_mock.mock_calls == [call()]
    assert emit_mock.ended_ok.mock_calls == [call()]


def test_run_ui_init_raises_craft_error(emit_mock, ui_init_mock, lifecycle_pack_mock):
    craft_error = CraftError("foo")
    ui_init_mock.side_effect = craft_error

    with pytest.raises(SystemExit):
        run(["rockcraft", "pack"])

    assert ui_init_mock.mock_calls == [call(["rockcraft", "pack"])]
    assert emit_mock.error.mock_calls == [call(craft_error)]
    assert lifecycle_pack_mock.mock_calls == []
    assert emit_mock.ended_ok.mock_calls == [call()]
