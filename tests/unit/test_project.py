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
import textwrap
from pathlib import Path
from typing import Any, Dict

import pydantic
import pytest
import yaml
from craft_application.models import BuildInfo
from craft_providers.bases import BaseName

from rockcraft.errors import ProjectLoadError, ProjectValidationError
from rockcraft.models import Project, load_project
from rockcraft.models.project import INVALID_NAME_MESSAGE, Platform
from rockcraft.pebble import Service

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
environment:
    BAZ: value1
    FOO: value3
    BAR: value2

package-repositories:
    - type: apt
      ppa: ppa/ppa

platforms:
    {BUILD_ON_ARCH}:
    some-text:
        build-on: [{BUILD_ON_ARCH}]
        build-for: {BUILD_ON_ARCH}
    same-with-different-syntax:
        build-on: [{BUILD_ON_ARCH}]
        build-for: [{BUILD_ON_ARCH}]
services:
    hello:
        override: replace
        command: /bin/hello
        on-failure: restart

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
def pebble_part() -> Dict[str, Any]:
    return {
        "pebble": {
            "plugin": "nil",
            "stage-snaps": ["pebble/latest/stable"],
            "stage": ["bin/pebble"],
            "override-prime": "craftctl default\nmkdir -p var/lib/pebble/default/layers",
        }
    }


def test_project_unmarshal(check, yaml_loaded_data):
    project = Project.unmarshal(yaml_loaded_data)

    for attr, v in yaml_loaded_data.items():
        if attr == "license":
            # The var license is a built-in,
            # so we workaround it by using an alias
            attr = "rock_license"

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
        if attr == "services":
            # Services are classes and not Dicts upfront
            v["hello"] = Service(**v["hello"])

        check.equal(getattr(project, attr.replace("-", "_")), v)


def test_unmarshal_no_repositories(yaml_loaded_data):
    yaml_loaded_data["package-repositories"] = None

    project = Project.unmarshal(yaml_loaded_data)

    assert project.package_repositories == []


def test_unmarshal_undefined_repositories(yaml_loaded_data):
    del yaml_loaded_data["package-repositories"]

    project = Project.unmarshal(yaml_loaded_data)

    assert project.package_repositories is None


def test_unmarshal_invalid_repositories(yaml_loaded_data):
    yaml_loaded_data["package-repositories"] = [{}]

    with pytest.raises(ProjectValidationError) as error:
        Project.unmarshal(yaml_loaded_data)

    assert error.value.args[0] == (
        "Bad rockcraft.yaml content:\n"
        "- field 'type' required in 'package-repositories' configuration\n"
        "- field 'url' required in 'package-repositories' configuration\n"
        "- field 'key-id' required in 'package-repositories' configuration"
    )


@pytest.mark.parametrize(
    "unsupported_field",
    [{"entrypoint": ["/bin/hello"]}, {"cmd": ["world"]}, {"env": ["foo=bar"]}],
)
def test_project_unmarshal_with_unsupported_fields(unsupported_field, yaml_loaded_data):
    loaded_data_with_unsupported_fields = {**yaml_loaded_data, **unsupported_field}
    with pytest.raises(ProjectValidationError) as err:
        _ = Project.unmarshal(loaded_data_with_unsupported_fields)

    assert (
        "All ROCKs have Pebble as their entrypoint, so you must use "
        "'services' to define your container application" in str(err.value)
    )


@pytest.mark.parametrize(
    "variable,is_forbidden",
    [("$BAR", True), ("BAR_$BAZ", True), ("BAR$", False)],
)
def test_forbidden_env_var_interpolation(
    check, yaml_loaded_data, variable, is_forbidden
):
    yaml_loaded_data["environment"]["foo"] = variable

    if is_forbidden:
        with pytest.raises(ProjectValidationError) as err:
            Project.unmarshal(yaml_loaded_data)
            check.equal(
                str(err.value), f"String interpolation not allowed for: {variable}"
            )
    else:
        project = Project.unmarshal(yaml_loaded_data)
        check.is_in("foo", project.environment)


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


def test_project_title_empty_invalid_name(yaml_loaded_data):
    """Test that an invalid name doesn't break the validation of the title."""
    yaml_loaded_data.pop("title")
    yaml_loaded_data["name"] = "my@rock"
    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_loaded_data)
    assert "Invalid name for ROCK" in str(err.value)


def test_project_build_base(yaml_loaded_data):
    yaml_loaded_data["build-base"] = "ubuntu:18.04"

    project = Project.unmarshal(yaml_loaded_data)
    assert project.base == "ubuntu:20.04"
    assert project.build_base == "ubuntu:18.04"


@pytest.mark.parametrize(
    ["base", "build_base", "expected_base", "expected_build_base"],
    [
        ("ubuntu:22.04", None, "ubuntu@22.04", "ubuntu@22.04"),
        ("ubuntu:22.04", "ubuntu:20.04", "ubuntu@22.04", "ubuntu@20.04"),
    ],
)
def test_project_base_colon(
    yaml_loaded_data, emitter, base, build_base, expected_base, expected_build_base
):
    """Test converting ":" to "@" in supported bases, and that warnings are emitted."""
    yaml_loaded_data["base"] = base
    yaml_loaded_data["build-base"] = build_base

    project = Project.unmarshal(yaml_loaded_data)

    assert project.base == expected_base
    assert project.build_base == expected_build_base

    emitter.assert_message(
        f'Warning: use of ":" in field "base" is deprecated. Prefer "{expected_base}" instead.'
    )
    if build_base is not None:
        emitter.assert_message(
            f'Warning: use of ":" in field "build_base" is deprecated. Prefer "{expected_build_base}" instead.'
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


@pytest.mark.parametrize("valid_name", ("aaa", "a00", "a-00", "a-a-a", "a-000-bbb"))
def test_project_name_valid(yaml_loaded_data, valid_name):
    yaml_loaded_data["name"] = valid_name

    project = Project.unmarshal(yaml_loaded_data)
    assert project.name == valid_name


@pytest.mark.parametrize(
    "invalid_name", ("AAA", "0aaa", "a", "a--a", "aa-", "a:a", "a/a", "a@a", "a_a")
)
def test_project_name_invalid(yaml_loaded_data, invalid_name):
    yaml_loaded_data["name"] = invalid_name

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_loaded_data)

    expected_message = f"{INVALID_NAME_MESSAGE} in field 'name'"
    assert expected_message in str(err.value)


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


@pytest.mark.parametrize(
    "packages,script",
    [
        (["pkg"], None),
        ([], "ls"),
    ],
)
def test_project_bare_overlay(yaml_loaded_data, packages, script):
    """Test that the combination of 'bare' base with an overlay-using part is blocked."""
    yaml_loaded_data["base"] = "bare"
    yaml_loaded_data["build-base"] = "ubuntu:22.04"

    foo_part = yaml_loaded_data["parts"]["foo"]
    foo_part["overlay-packages"] = packages
    foo_part["overlay-script"] = script

    with pytest.raises(ProjectValidationError) as err:
        Project.unmarshal(yaml_loaded_data)
    assert str(err.value) == (
        'Overlays cannot be used with "bare" bases (there is no system to overlay).'
    )


def test_project_load(check, yaml_data, yaml_loaded_data, pebble_part, tmp_path):
    rockcraft_file = tmp_path / "rockcraft.yaml"
    rockcraft_file.write_text(
        yaml_data,
        encoding="utf-8",
    )

    # The Pebble part should be added to the loaded data
    yaml_loaded_data["parts"].update(pebble_part)

    project_yaml = load_project(rockcraft_file)
    check.equal(project_yaml, yaml_loaded_data)

    # Test that the environment variables are loaded in the right order
    expected_ordered_environment = {"BAZ": "value1", "FOO": "value3", "BAR": "value2"}
    check.equal(project_yaml["environment"], expected_ordered_environment)


def test_project_unmarshal_existing_pebble(tmp_path):
    """Test that trying to load a project that already has a "pebble" part fails."""
    yaml_data = textwrap.dedent(
        """
        name: pebble-part
        title: Rock with Pebble
        version: latest
        base: ubuntu:20.04
        summary: Rock with Pebble
        description: Rock with Pebble
        license: Apache-2.0
        platforms:
            amd64:

        parts:
            foo:
                plugin: nil
                overlay-script: ls
            pebble:
                plugin: go
                source: https://github.com/fork/pebble.git
                source-branch: new-pebble-work
    """
    )
    rockcraft_file = tmp_path / "rockcraft.yaml"
    rockcraft_file.write_text(
        yaml_data,
        encoding="utf-8",
    )

    with pytest.raises(ProjectValidationError):
        Project.unmarshal(load_project(rockcraft_file))


def test_project_load_error():
    with pytest.raises(ProjectLoadError) as err:
        load_project(Path("does_not_exist.txt"))
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


EXPECTED_DUMPED_YAML = f"""\
name: mytest
title: My Test
version: latest
summary: example for unit tests
description: this is an example of a rockcraft.yaml for the purpose of testing rockcraft
base: ubuntu:20.04
license: Apache-2.0
parts:
  foo:
    plugin: nil
    overlay-script: ls
platforms:
  {BUILD_ON_ARCH}:
    build_on: null
    build_for: null
  some-text:
    build_on:
    - {BUILD_ON_ARCH}
    build_for:
    - {BUILD_ON_ARCH}
  same-with-different-syntax:
    build_on:
    - {BUILD_ON_ARCH}
    build_for:
    - {BUILD_ON_ARCH}
build-base: ubuntu:20.04
environment:
  BAZ: value1
  FOO: value3
  BAR: value2
services:
  hello:
    override: replace
    command: /bin/hello
    on-failure: restart
package-repositories:
- type: apt
  ppa: ppa/ppa
"""


def test_project_yaml(yaml_loaded_data):
    project = Project.unmarshal(yaml_loaded_data)
    assert project.to_yaml() == EXPECTED_DUMPED_YAML


@pytest.mark.parametrize(
    ["platforms", "expected_build_infos"],
    [
        (
            {
                "amd64": None,
            },
            [
                BuildInfo(
                    build_on="amd64",
                    build_for="amd64",
                    base=BaseName(name="ubuntu", version="20.04"),
                    platform="amd64",
                )
            ],
        ),
        (
            {
                "amd64": {
                    "build-on": ["amd64", "i386"],
                    "build-for": ["amd64"],
                },
            },
            [
                BuildInfo(
                    build_on="amd64",
                    build_for="amd64",
                    base=BaseName(name="ubuntu", version="20.04"),
                    platform="amd64",
                ),
                BuildInfo(
                    build_on="i386",
                    build_for="amd64",
                    base=BaseName(name="ubuntu", version="20.04"),
                    platform="amd64",
                ),
            ],
        ),
        (
            {
                "amd64v2": {
                    "build-on": ["amd64"],
                    "build-for": "amd64",
                },
            },
            [
                BuildInfo(
                    build_on="amd64",
                    build_for="amd64",
                    base=BaseName(name="ubuntu", version="20.04"),
                    platform="amd64v2",
                )
            ],
        ),
    ],
)
def test_project_get_build_plan(yaml_loaded_data, platforms, expected_build_infos):
    yaml_loaded_data["platforms"] = platforms
    project = Project.unmarshal(yaml_loaded_data)
    assert project.get_build_plan() == expected_build_infos
