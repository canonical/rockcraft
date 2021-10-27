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

from pathlib import Path
from unittest.mock import call

import pytest

import rockcraft
from rockcraft import ui


def test_init_defaults(emit_mock):
    ui.init(["rockcraft", "pack"])

    assert emit_mock.init.mock_calls == [
        call(
            mode=ui.EmitterMode.NORMAL,
            appname="rockcraft",
            greeting=f"Rockcraft version {rockcraft.__version__}.",
        )
    ]


def test_init_verbose(emit_mock):
    ui.init(["rockcraft", "pack", "--verbose"])

    assert emit_mock.init.mock_calls == [
        call(
            mode=ui.EmitterMode.VERBOSE,
            appname="rockcraft",
            greeting=f"Rockcraft version {rockcraft.__version__}.",
        )
    ]


def test_init_managed_mode(mocker, emit_mock):
    mocker.patch("rockcraft.utils.is_managed_mode", return_value=True)

    ui.init(["rockcraft", "pack", "--verbose"])

    assert emit_mock.init.mock_calls == [
        call(
            mode=ui.EmitterMode.VERBOSE,
            appname="rockcraft",
            greeting=f"Rockcraft version {rockcraft.__version__}.",
            log_filepath=Path("/tmp/rockcraft.log"),
        )
    ]


def test_init_only_pack():
    with pytest.raises(ui.CraftError) as craft_error:
        ui.init(["rockcraft", "p"])

    assert str(craft_error.value) == "Only pack is supported."


def test_init_pack_only_verbose():
    with pytest.raises(ui.CraftError) as craft_error:
        ui.init(["rockcraft", "pack", "--not-verbose"])

    assert str(craft_error.value) == "Only option supported for pack is '--verbose'."
