# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
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
import yaml

from rockcraft.pebble import Pebble

ENVIRONMENT_YAML = """\
name: environment-test
version: 2.0
base: ubuntu:20.04
summary: Environment
description: A rock with an environment but no real purpose
license: Apache-2.0
environment:
  FOO: bar
  X: "override me"
services:
  test:
    override: replace
    command: /usr/bin/env
    startup: enabled
    environment:
      X: "ship it!"
      CRAFT_VAR: $CRAFT_PROJECT_VERSION

platforms:
  amd64:

parts:
  part1:
    plugin: nil
"""


def test_application_expand_environment(new_dir, default_application):
    project_file = Path(new_dir) / "rockcraft.yaml"
    project_file.write_text(ENVIRONMENT_YAML)

    project = default_application.project

    assert project.services["test"].environment == {
        "X": "ship it!",
        "CRAFT_VAR": "2.0",
    }


@pytest.mark.parametrize(
    ("base", "build_base", "expected_spec"),
    [
        # 24.04 and beyond: pebble exists in usr/bin/
        ("bare", "devel", Pebble.PEBBLE_PART_SPEC),
        ("ubuntu@24.04", "devel", Pebble.PEBBLE_PART_SPEC),
        # 20.04 and 22.04: pebble exists in bin/
        ("ubuntu@20.04", None, Pebble.PEBBLE_PART_SPEC_PREVIOUS),
        ("ubuntu@22.04", None, Pebble.PEBBLE_PART_SPEC_PREVIOUS),
        ("ubuntu@20.04", "ubuntu@20.04", Pebble.PEBBLE_PART_SPEC_PREVIOUS),
        ("ubuntu@22.04", "ubuntu@22.04", Pebble.PEBBLE_PART_SPEC_PREVIOUS),
    ],
)
def test_application_pebble_part(
    new_dir, default_application, base, build_base, expected_spec
):
    """Test that loading the project through the application adds the Pebble part."""
    project_file = Path(new_dir) / "rockcraft.yaml"
    new_yaml = yaml.safe_load(ENVIRONMENT_YAML)
    new_yaml["base"] = base
    new_yaml["build-base"] = build_base
    project_file.write_text(yaml.safe_dump(new_yaml))

    project = default_application.project
    assert project.parts["pebble"] == expected_spec
