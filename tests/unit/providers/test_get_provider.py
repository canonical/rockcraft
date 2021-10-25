# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021 Canonical Ltd.
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

import sys

from rockcraft.providers import LXDProvider, MultipassProvider, get_provider


def test_get_provider_default():
    if sys.platform == "linux":
        assert isinstance(get_provider(), LXDProvider)
    else:
        assert isinstance(get_provider(), MultipassProvider)


def test_get_provider_developer_env(monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_PROVIDER", "lxd")
    assert isinstance(get_provider(), LXDProvider)

    monkeypatch.setenv("ROCKCRAFT_PROVIDER", "multipass")
    assert isinstance(get_provider(), MultipassProvider)
