# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2025 Canonical Ltd.
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
"""Unit tests for the ProjectService."""

import craft_platforms
import pytest
from rockcraft.pebble import Pebble
from rockcraft.services.project import RockcraftProjectService


@pytest.mark.parametrize(
    ("base", "build_base"),
    [
        ("bare", "ubuntu@20.04"),
        ("bare", "ubuntu@22.04"),
        ("ubuntu@20.04", None),
        ("ubuntu@22.04", None),
        ("ubuntu@20.04", "ubuntu@20.04"),
        ("ubuntu@22.04", "ubuntu@22.04"),
    ],
)
@pytest.mark.parametrize(
    "parts", [{}, {"pebble": Pebble.PEBBLE_PART_PEBBLE_IN_BIN.copy()}]
)
def test_add_pebble_part_project_jammy_focal(
    base,
    build_base,
    parts,
    fake_host_architecture: craft_platforms.DebianArchitecture,
):
    project = {
        "base": base,
        "build-base": build_base,
        "parts": parts,
    }

    RockcraftProjectService._app_preprocess_project(
        project=project,
        build_on=fake_host_architecture.value,
        build_for="Unused",
        platform="Unused",
    )

    assert project["parts"]["pebble"] == Pebble.PEBBLE_PART_PEBBLE_IN_BIN


@pytest.mark.parametrize(
    ("base", "build_base"),
    [
        ("bare", "ubuntu@24.04"),
        ("ubuntu@24.04", None),
    ],
)
@pytest.mark.parametrize(
    "parts", [{}, {"pebble": Pebble.PEBBLE_PART_PEBBLE_ORGANIZED_USR_BIN.copy()}]
)
def test_add_pebble_part_noble(
    base,
    build_base,
    parts,
    fake_host_architecture: craft_platforms.DebianArchitecture,
):
    project = {
        "base": base,
        "build-base": build_base,
        "parts": parts,
    }

    RockcraftProjectService._app_preprocess_project(
        project=project,
        build_on=fake_host_architecture.value,
        build_for="Unused",
        platform="Unused",
    )

    assert project["parts"]["pebble"] == Pebble.PEBBLE_PART_PEBBLE_ORGANIZED_USR_BIN


@pytest.mark.parametrize(
    ("base", "build_base"),
    [
        ("bare", "devel"),
        ("ubuntu@25.10", "devel"),
    ],
)
@pytest.mark.parametrize("parts", [{}, {"pebble": Pebble.PEBBLE_PART_SPEC.copy()}])
def test_add_pebble_part_questing_or_newer(
    base,
    build_base,
    parts,
    fake_host_architecture: craft_platforms.DebianArchitecture,
):
    project = {
        "base": base,
        "build-base": build_base,
        "parts": parts,
    }

    RockcraftProjectService._app_preprocess_project(
        project=project,
        build_on=fake_host_architecture.value,
        build_for="Unused",
        platform="Unused",
    )

    assert project["parts"]["pebble"] == Pebble.PEBBLE_PART_SPEC


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
  EXPANDED: $CRAFT_PROJECT_NAME
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


@pytest.mark.parametrize("fake_project_yaml", [ENVIRONMENT_YAML])
@pytest.mark.usefixtures("fake_project_file")
def test_services_environment_expanded(fake_services):
    project_service = fake_services.get("project")
    project_service.configure(platform=None, build_for=None)

    project = project_service.get()

    assert project.services["test"].environment == {
        "X": "ship it!",
        "CRAFT_VAR": "2.0",
    }

    assert project.environment == {
        "FOO": "bar",
        "X": "override me",
        "EXPANDED": "environment-test",
    }


@pytest.mark.usefixtures("fake_project_file", "project_keys")
@pytest.mark.parametrize(
    "project_keys",
    [
        {
            "base": "ubuntu@25.10",
            "build-base": "devel",
            "parts": {
                "empty": {
                    "plugin": "nil",
                }
            },
        }
    ],
    indirect=True,
)
def test_project_service_devel_bases(fake_services):
    project_service = fake_services.get("project")
    project_service.configure(platform=None, build_for=None)

    assert not project_service.is_effective_base_eol()
    assert project_service.check_base_is_supported("pack") is None
    assert project_service.base_eol_soon_date() is None
