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

import textwrap
from pathlib import Path

import pytest

from rockcraft.project import (
    Project,
    ProjectLoadError,
    ProjectValidationError,
    load_project,
)


@pytest.fixture
def yaml_data():
    return {
        "name": "mytest",
        "version": "latest",
        "title": "My Test ROCK",
        "summary": "This is a test ROCK",
        "description": "This ROCK is non functional \
            and entirely dedicated to Rockcraft's \
            unit tests",
        "contact": ["foo@bar.com", "https://me.i/contact"],
        "issues": "https://github.com/canonical/rockcraft/issues",
        "source-code": "https://github.com/canonical/rockcraft",
        "website": "https://github.com/canonical/rockcraft",
        "docs": "https://rockcraft.readthedocs.io/en/latest/index.html",
        "license": "Apache-2.0",
        "support": {
            "end-of-life": "2027-04-01",
            "end-of-support": "2027-04-01T00:00:00Z",
            "info": "https://ubuntu.com/support"
        },
        "base": "ubuntu:20.04",
        "entrypoint": ["/bin/hello"],
        "cmd": ["world"],
        "env": [{"NAME": "VALUE"}],
        "parts": {
            "foo": {
                "plugin": "nil",
                "overlay-script": "ls",
            }
        },
    }


def test_project_unmarshal(yaml_data):
    project = Project.unmarshal(yaml_data)

    assert project.name == "mytest"
    assert project.version == "latest"
    assert project.base == "ubuntu:20.04"
    assert project.build_base == "ubuntu:20.04"
    assert project.entrypoint == ["/bin/hello"]
    assert project.cmd == ["world"]
    assert project.env == [{"NAME": "VALUE"}]
    assert project.parts == {
        "foo": {
            "plugin": "nil",
            "overlay-script": "ls",
        }
    }


@pytest.mark.parametrize("base", ["ubuntu:18.04", "ubuntu:20.04"])
def test_project_base(yaml_data, base):
    yaml_data["base"] = base

    project = Project.unmarshal(yaml_data)
    assert project.base == base
    assert project.build_base == base


def test_project_base_invalid(yaml_data):
    yaml_data["base"] = "ubuntu:19.04"

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_data)
    assert str(err.value) == (
        "Bad rockcraft.yaml content:\n"
        "- unexpected value; permitted: 'ubuntu:18.04', 'ubuntu:20.04' in field 'base'"
    )


def test_project_build_base(yaml_data):
    yaml_data["build-base"] = "ubuntu:18.04"

    project = Project.unmarshal(yaml_data)
    assert project.base == "ubuntu:20.04"
    assert project.build_base == "ubuntu:18.04"


@pytest.mark.parametrize("field", ["name", "version", "base", "parts"])
def test_project_missing_field(yaml_data, field):
    del yaml_data[field]

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_data)
    assert str(err.value) == (
        "Bad rockcraft.yaml content:\n"
        f"- field '{field}' required in top-level configuration"
    )


def test_project_extra_field(yaml_data):
    yaml_data["extra"] = "invalid"

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_data)
    assert str(err.value) == (
        "Bad rockcraft.yaml content:\n"
        "- extra field 'extra' not permitted in top-level configuration"
    )


def test_project_parts_validation(yaml_data):
    yaml_data["parts"]["foo"]["invalid"] = True

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_data)
    assert str(err.value) == (
        "Bad rockcraft.yaml content:\n"
        "- extra field 'invalid' not permitted in 'parts.foo' configuration"
    )


def test_project_load(new_dir):
    Path("rockcraft.yaml").write_text(
        textwrap.dedent(
            """
            name: mytest
            version: latest
            base: ubuntu:20.04
            build-base: ubuntu:20.04
            title: My Test ROCK
            summary: This is a test ROCK
            description: |
                This ROCK is non functional
                and entirely dedicated to Rockcraft's
                unit tests
            contact: [foo@bar.com, https://me.i/contact]
            issues: https://github.com/canonical/rockcraft/issues
            source-code: https://github.com/canonical/rockcraft
            website: https://github.com/canonical/rockcraft
            docs: https://rockcraft.readthedocs.io/en/latest/index.html
            license: Apache-2.0
            support:
                end-of-life: "2027-04-01"
                end-of-support: "2027-04-01T00:00:00Z"
                info: https://ubuntu.com/support
            parts:
              foo:
                plugin: nil
                overlay-script: "ls"
            """
        ),
        encoding="utf-8",
    )

    project = load_project("rockcraft.yaml")

    assert project.name == "mytest"
    assert project.version == "latest"
    assert project.base == "ubuntu:20.04"
    assert project.build_base == "ubuntu:20.04"
    assert project.title == "My Test ROCK"
    assert project.summary == "This is a test ROCK"
    assert project.description == '''This ROCK is non functional
and entirely dedicated to Rockcraft's
unit tests
'''
    assert project.contact == ["foo@bar.com", "https://me.i/contact"]
    assert project.issues == "https://github.com/canonical/rockcraft/issues"
    assert project.source_code == "https://github.com/canonical/rockcraft"
    assert project.website == "https://github.com/canonical/rockcraft"
    assert project.docs == "https://rockcraft.readthedocs.io/en/latest/index.html"
    assert project.license == "Apache-2.0"
    assert project.support.end_of_life == "2027-04-01"
    assert project.support.end_of_support == "2027-04-01T00:00:00Z"
    assert project.support.info == "https://ubuntu.com/support"
    assert project.parts == {
        "foo": {
            "plugin": "nil",
            "overlay-script": "ls",
        }
    }


def test_project_load_error():
    with pytest.raises(ProjectLoadError) as err:
        load_project("does_not_exist.txt")
    assert str(err.value) == "No such file or directory: 'does_not_exist.txt'."


# TODO: add additional validation and formatting tests
