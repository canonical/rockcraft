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

import datetime
import os
import subprocess
from unittest.mock import patch

import pydantic
import pytest
import yaml

from rockcraft.errors import ProjectLoadError, ProjectValidationError
from rockcraft.project import ArchitectureMapping, Platform, Project, load_project

_ARCH_MAPPING = {"x86": "amd64", "x64": "amd64"}
try:
    _RUNNER_ARCH = os.environ["RUNNER_ARCH"].lower()
except KeyError:
    # When not running as a GitHub workflow,
    # it can only run on Linux
    _RUNNER_ARCH = (
        subprocess.check_output(["dpkg", "--print-architecture"])
        .decode()
        .strip()
        .lower()
    )
BUILD_ON_ARCH = _ARCH_MAPPING.get(_RUNNER_ARCH, _RUNNER_ARCH)


ROCKCRAFT_YAML = f"""---
name: mytest
title: My Test
version: latest
base: ubuntu:20.04
summary: "example for unit tests"
description: "this is an example of a rockcraft.yaml for the purpose of testing rockcraft"
license: Apache-2.0
entrypoint: ["/bin/hello"]
cmd: ["world"]
env:
    - NAME: "VALUE"
platforms:
    {BUILD_ON_ARCH}:
    some-text:
        build-on: [{BUILD_ON_ARCH}]
        build-for: {BUILD_ON_ARCH}
    same-with-different-syntax:
        build-on: [{BUILD_ON_ARCH}]
        build-for: [{BUILD_ON_ARCH}]

parts:
    foo:
        plugin: nil
        overlay-script: ls
"""


@pytest.fixture
def yaml_data():
    return ROCKCRAFT_YAML


@pytest.fixture
def yaml_loaded_data():
    return yaml.safe_load(ROCKCRAFT_YAML)


@pytest.fixture
def pebble_part():
    return {
        "pebble": {
            "plugin": "go",
            "source": "https://github.com/canonical/pebble.git",
            "build-snaps": ["go/1.19/stable"],
            "override-build": "go mod download\n"
            "CGO_ENABLED=0 go build -o pebble ./cmd/pebble\n"
            'install -D -m755 pebble "$CRAFT_PART_INSTALL"/bin/pebble\n',
        }
    }


def test_project_unmarshal(yaml_loaded_data, pebble_part):
    project = Project.unmarshal(yaml_loaded_data)

    assert project.name == "mytest"
    assert project.title == "My Test"
    assert project.version == "latest"
    assert project.base == "ubuntu:20.04"
    assert project.summary == "example for unit tests"
    assert (
        project.description
        == "this is an example of a rockcraft.yaml for the purpose of testing rockcraft"
    )
    assert project.rock_license == "Apache-2.0"
    assert project.build_base == "ubuntu:20.04"
    assert project.entrypoint == ["/bin/hello"]
    assert project.cmd == ["world"]
    assert project.env == [{"NAME": "VALUE"}]
    assert project.parts == {
        **{
            "foo": {
                "plugin": "nil",
                "overlay-script": "ls",
            }
        },
        **pebble_part,
    }


@pytest.mark.parametrize("base", ["ubuntu:18.04", "ubuntu:20.04"])
def test_project_base(yaml_loaded_data, base):
    yaml_loaded_data["base"] = base

    project = Project.unmarshal(yaml_loaded_data)
    assert project.base == base
    assert project.build_base == base


def test_project_base_invalid(yaml_loaded_data):
    yaml_loaded_data["base"] = "ubuntu:19.04"

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_loaded_data)
    assert str(err.value) == (
        "Bad rockcraft.yaml content:\n"
        "- unexpected value; permitted: 'bare', 'ubuntu:18.04', 'ubuntu:20.04', 'ubuntu:22.04' in field 'base'"
    )


def test_project_license_invalid(yaml_loaded_data):
    yaml_loaded_data["license"] = "apache 0.x"

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_loaded_data)
    assert str(err.value) == (
        f"License {yaml_loaded_data['license']} not valid. It must be valid and in SPDX format."
    )


def test_project_license_clean_name(yaml_loaded_data):
    yaml_loaded_data["license"] = "mIt"

    project = Project.unmarshal(yaml_loaded_data)
    assert project.rock_license == "MIT"


def test_project_title_empty(yaml_loaded_data):
    yaml_loaded_data.pop("title")

    project = Project.unmarshal(yaml_loaded_data)
    assert project.title == project.name


def test_project_build_base(yaml_loaded_data):
    yaml_loaded_data["build-base"] = "ubuntu:18.04"

    project = Project.unmarshal(yaml_loaded_data)
    assert project.base == "ubuntu:20.04"
    assert project.build_base == "ubuntu:18.04"


def test_architecture_mapping():
    _ = ArchitectureMapping(
        description="mock arch",
        deb_arch="amd64",
        compatible_uts_machine_archs=["x86_64"],
        go_arch="amd64",
    )


def test_project_platform_invalid():
    def load_platform(platform, raises):
        with pytest.raises(raises) as err:
            Platform(**platform)

        return str(err.value)

    # build_on must be a list
    mock_platform = {"build-on": "amd64"}
    assert "not a valid list" in load_platform(mock_platform, pydantic.ValidationError)

    # lists must be unique
    mock_platform = {"build-on": ["amd64", "amd64"]}
    assert "duplicated" in load_platform(mock_platform, pydantic.ValidationError)

    mock_platform = {"build-for": ["amd64", "amd64"]}
    assert "duplicated" in load_platform(mock_platform, pydantic.ValidationError)

    # build-for must be only 1 element (NOTE: this may change)
    mock_platform = {"build-on": ["amd64"], "build-for": ["amd64", "arm64"]}
    assert "multiple target architectures" in load_platform(
        mock_platform, ProjectValidationError
    )

    # If build_for is provided, then build_on must also be
    mock_platform = {"build-for": ["arm64"]}
    assert "'build_for' expects 'build_on' to also be provided." in load_platform(
        mock_platform, ProjectValidationError
    )


@patch("platform.machine")
def test_project_platform_variants(mock_uts_machine, yaml_loaded_data):
    def load_project_for_arch(uts_arch: str, arch: str) -> Project:
        mock_uts_machine.return_value = uts_arch
        yaml_loaded_data["platforms"] = {arch: None}
        return Project.unmarshal(yaml_loaded_data)

    # arm/v7
    assert (
        load_project_for_arch("arm", "arm").platforms["arm"]["build_for_variant"]
        == "v7"
    )

    # arm64/v8
    assert (
        load_project_for_arch("aarch64", "arm64").platforms["arm64"][
            "build_for_variant"
        ]
        == "v8"
    )

    # others
    assert (
        load_project_for_arch("x86_64", "amd64")
        .platforms["amd64"]
        .get("build_for_variant")
        is None
    )


def test_project_all_platforms_invalid(yaml_loaded_data):
    def reload_project_platforms(new_platforms=None):
        if new_platforms:
            yaml_loaded_data["platforms"] = mock_platforms
        with pytest.raises(ProjectValidationError) as err:
            Project.unmarshal(yaml_loaded_data)

        return str(err.value)

    # A platform validation error must have an explicit prefix indicating
    # the platform entry for which the validation has failed
    mock_platforms = {"foo": {"build-for": ["amd64"]}}
    assert "'foo': 'build_for' expects 'build_on'" in reload_project_platforms(
        mock_platforms
    )

    # If the label maps to a valid architecture and
    # `build-for` is present, then both need to have the same value    mock_platforms = {"mock": {"build-on": "amd64"}}
    mock_platforms = {"arm64": {"build-on": ["arm64"], "build-for": ["amd64"]}}
    assert "arm64 != amd64" in reload_project_platforms(mock_platforms)

    # Both build and target architectures must be supported
    mock_platforms = {
        "mock": {"build-on": ["arm64a", "noarch"], "build-for": ["amd64"]}
    }
    assert "none of these build architectures is supported" in reload_project_platforms(
        mock_platforms
    )

    mock_platforms = {
        "mock": {"build-on": ["arm64a", "arm64"], "build-for": ["noarch"]}
    }
    assert "build ROCK for target architecture noarch" in reload_project_platforms(
        mock_platforms
    )

    # The underlying build machine must be compatible
    # with both build_on and build_for
    other_arch = "arm" if BUILD_ON_ARCH == "amd64" else "amd64"
    mock_platforms = {"mock": {"build-on": [other_arch], "build-for": other_arch}}
    assert "if the host is compatible with" in reload_project_platforms(mock_platforms)

    mock_platforms = {"mock": {"build-on": [other_arch], "build-for": "amd64"}}
    assert (
        f"must be built on one of the following architectures: {[other_arch]}"
        in reload_project_platforms(mock_platforms)
    )


@pytest.mark.parametrize(
    "field", ["name", "version", "base", "parts", "description", "summary", "license"]
)
def test_project_missing_field(yaml_loaded_data, field):
    del yaml_loaded_data[field]

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_loaded_data)
    assert str(err.value) == (
        "Bad rockcraft.yaml content:\n"
        f"- field '{field}' required in top-level configuration"
    )


def test_project_extra_field(yaml_loaded_data):
    yaml_loaded_data["extra"] = "invalid"

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_loaded_data)
    assert str(err.value) == (
        "Bad rockcraft.yaml content:\n"
        "- extra field 'extra' not permitted in top-level configuration"
    )


def test_project_parts_validation(yaml_loaded_data):
    yaml_loaded_data["parts"]["foo"]["invalid"] = True

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_loaded_data)
    assert str(err.value) == (
        "Bad rockcraft.yaml content:\n"
        "- extra field 'invalid' not permitted in 'parts.foo' configuration"
    )


def test_project_load(yaml_data, yaml_loaded_data, pebble_part, tmp_path):
    rockcraft_file = tmp_path / "rockcraft.yaml"
    rockcraft_file.write_text(
        yaml_data,
        encoding="utf-8",
    )

    project = load_project(str(rockcraft_file))

    for attr, v in yaml_loaded_data.items():
        if attr == "license":
            # the var license is a built-in,
            # so we workaround it by using an alias
            attr = "rock_license"

        if attr == "parts":
            v = {**v, **pebble_part}
        if attr == "platforms":
            # platforms get mutated at validation time
            assert getattr(project, attr).keys() == v.keys()
            assert all(
                "build_on" in platform for platform in getattr(project, attr).values()
            )
            assert all(
                "build_for" in platform for platform in getattr(project, attr).values()
            )
            continue

        assert getattr(project, attr) == v


def test_project_load_error():
    with pytest.raises(ProjectLoadError) as err:
        load_project("does_not_exist.txt")
    assert str(err.value) == "No such file or directory: 'does_not_exist.txt'."


def test_project_generate_metadata(yaml_loaded_data):
    project = Project.unmarshal(yaml_loaded_data)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    digest = "a1b2c3"  # mock digest
    oci_annotations, rock_metadata = project.generate_metadata(
        now, bytes.fromhex(digest)
    )
    assert oci_annotations == {
        "org.opencontainers.image.version": yaml_loaded_data["version"],
        "org.opencontainers.image.title": yaml_loaded_data["title"],
        "org.opencontainers.image.ref.name": yaml_loaded_data["name"],
        "org.opencontainers.image.licenses": yaml_loaded_data["license"],
        "org.opencontainers.image.created": now,
        "org.opencontainers.image.base.digest": digest,
    }
    assert rock_metadata == {
        "name": yaml_loaded_data["name"],
        "summary": yaml_loaded_data["summary"],
        "title": yaml_loaded_data["title"],
        "version": yaml_loaded_data["version"],
        "created": now,
        "base": yaml_loaded_data["base"],
        "base-digest": digest,
    }


# TODO: add additional validation and formatting tests
