# Copyright 2021 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For further info, check https://github.com/canonical/charmcraft

import os
import pathlib
from unittest import mock

import pytest
from craft_providers import bases


@pytest.fixture(autouse=True)
def bypass_buildd_base_setup(monkeypatch):
    """Patch out inherited setup steps."""
    monkeypatch.setattr(bases.BuilddBase, "setup", lambda *args, **kwargs: None)


@pytest.fixture(autouse=True)
def clear_environment(monkeypatch):
    monkeypatch.setattr(os, "environ", {})


@pytest.fixture
def mock_path():
    mock_path = mock.Mock(spec=pathlib.Path)
    mock_path.stat.return_value.st_ino = 445566
    yield mock_path
