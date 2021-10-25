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

from unittest import mock

import pytest
from craft_providers import Executor

from rockcraft import ui


@pytest.fixture
def emit_mock():
    """Setup a fake emitter."""
    patcher = mock.patch.object(ui, "emit")
    yield patcher.start()
    patcher.stop()


@pytest.fixture
def mock_instance():
    """Provide a mock instance (Executor)."""
    yield mock.Mock(spec=Executor)
