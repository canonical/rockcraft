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
from dateutil import parser

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


def test_root_validation(yaml_data):
    project = Project.unmarshal(yaml_data)
    
    expected_annotations = [
        'org.opencontainers.image.version',
        'org.opencontainers.image.base.name',
        'org.opencontainers.image.created'
    ]
    
    assert hasattr(project, 'annotations')
    assert isinstance(project.annotations, dict)
    assert all(annot in project.annotations for annot in expected_annotations)
    assert project.annotations['org.opencontainers.image.version'] == yaml_data['version']
    assert project.annotations['org.opencontainers.image.base.name'] == yaml_data['base']
    try:
        parser.parse(project.annotations['org.opencontainers.image.created'])
    except parser._parser.ParserError as err:
        assert False, f'Wrong date format passed to the annotation org.opencontainers.image.created: {err}'
        
# TODO: add additional validation and formatting tests
