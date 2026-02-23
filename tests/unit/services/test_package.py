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
from typing import cast

import pytest
from craft_application import ServiceFactory
from craft_platforms import DebianArchitecture
from rockcraft.models import Project
from rockcraft.oci import Image
from rockcraft.services import RockcraftImageService, package


@pytest.mark.usefixtures("fake_project_file", "project_keys")
@pytest.mark.parametrize(
    "project_keys",
    [
        {
            "platforms": {
                "bob": {
                    "build-on": DebianArchitecture.from_host(),
                    "build-for": "s390x",
                }
            },
        },
    ],
)
def test_pack(fake_services: ServiceFactory, default_image_info, mocker):
    image_service = cast(RockcraftImageService, fake_services.get("image"))

    mock_obtain_image = mocker.patch.object(
        image_service, "obtain_image", return_value=default_image_info
    )
    mock_inner_pack = mocker.patch.object(package, "_pack")

    fake_services.get("project").configure(platform="bob", build_for="s390x")
    fake_services.get("package").pack(prime_dir=Path("prime"), dest=Path())

    # Check that the image service was queried for the ImageInfo
    mock_obtain_image.assert_called_once_with()

    # Check that the regular _pack() function was called with the correct
    # parameters.
    mock_inner_pack.assert_called_once_with(
        base_digest=b"deadbeef",
        base_layer_dir=Path(),
        build_for="s390x",
        prime_dir=Path("prime"),
        project=fake_services.get("project").get(),
        project_base_image=default_image_info.base_image,
        rock_suffix="bob",
    )


@pytest.mark.usefixtures("fake_project_file", "project_keys")
@pytest.mark.parametrize(
    ("project_keys", "expected_entrypoint", "expected_cmd"),
    [
        # Most common scenario
        (
            {
                "run_user": "_daemon_",
                "environment": {"test": "foo"},
                "services": {"test": {"override": "replace", "command": "echo foo"}},
            },
            ["/usr/bin/pebble", "enter"],
            [],
        ),
        # Most common scenario (22.04 base, different pebble location)
        (
            {
                "base": "ubuntu@22.04",
                "run_user": "_daemon_",
                "environment": {"test": "foo"},
                "services": {"test": {"override": "replace", "command": "echo foo"}},
            },
            ["/bin/pebble", "enter"],
            [],
        ),
        # Entrypoint service set
        (
            {
                "run_user": "_daemon_",
                "environment": {"test": "foo"},
                "services": {
                    "test": {"override": "replace", "command": "echo [ foo ]"}
                },
                "entrypoint_service": "test",
            },
            ["/usr/bin/pebble", "enter", "--args", "test"],
            ["foo"],
        ),
        # Entrypoint command set
        (
            {
                "run_user": "_daemon_",
                "environment": {"test": "foo"},
                "services": {"test": {"override": "replace", "command": "echo foo"}},
                "entrypoint_command": "echo [ foo ]",
            },
            ["echo"],
            ["foo"],
        ),
        # Entrypoint command with no CMD
        (
            {
                "run_user": "_daemon_",
                "environment": {"test": "foo"},
                "services": {"test": {"override": "replace", "command": "echo foo"}},
                "entrypoint_command": "echo",
            },
            ["echo"],
            None,
        ),
        # Entrypoint command with only CMD
        (
            {
                "run_user": "_daemon_",
                "environment": {"test": "foo"},
                "services": {"test": {"override": "replace", "command": "echo foo"}},
                "entrypoint_command": "[ echo foo ]",
            },
            [],
            ["echo", "foo"],
        ),
        # Empty entrypoint command
        (
            {
                "run_user": "_daemon_",
                "environment": {"test": "foo"},
                "services": {"test": {"override": "replace", "command": "echo foo"}},
                "entrypoint_command": "[ ]",
            },
            [],
            [],
        ),
        # Entrypoint command edge case
        (
            {
                "run_user": "_daemon_",
                "environment": {"test": "foo"},
                "services": {"test": {"override": "replace", "command": "echo foo"}},
                "entrypoint_command": "echo '[ foo ]' [ bar ]",
            },
            ["echo", "[ foo ]"],
            ["bar"],
        ),
    ],
)
def test_inner_pack(
    fake_services: ServiceFactory, mocker, expected_entrypoint, expected_cmd
):
    fake_services.get("project").configure(platform=None, build_for=None)
    project = cast(Project, fake_services.get("project").get())

    # Vars for reuse
    tag = cast(str, project.version)
    base_layer_dir = Path()
    prime_dir = Path("prime")
    annotations = {"annotation": "foo"}
    metadata = {"metadata": "bar"}

    # Mock the resulting image and the functions called
    image = mocker.create_autospec(Image, instance=True)
    image.add_layer.return_value = image

    # Mock generate metadata function
    mocker.patch.object(
        Project, "generate_metadata", return_value=(annotations, metadata)
    )

    # Call the internal pack function
    package._pack(
        base_digest=b"deadbeef",
        base_layer_dir=base_layer_dir,
        build_for="amd64",
        prime_dir=prime_dir,
        project=project,
        project_base_image=image,
        rock_suffix="test-rock",
    )

    # Assertions
    image.add_layer.assert_called_once_with(
        tag=tag, new_layer_dir=prime_dir, base_layer_dir=base_layer_dir
    )

    image.add_user.assert_called_once_with(
        prime_dir=prime_dir,
        base_layer_dir=base_layer_dir,
        tag=tag,
        username=project.run_user,
        uid=584792,
    )
    image.set_default_user.assert_called_once_with(584792, project.run_user)
    image.set_entrypoint.assert_called_once_with(expected_entrypoint)
    image.set_cmd.assert_called_once_with(expected_cmd)
    image.set_default_path.assert_called_once_with(project.base)
    image.set_pebble_layer.assert_called_once_with(
        services=project.marshal().get("services", {}),
        checks=project.marshal().get("checks", {}),
        name=project.name,
        tag=tag,
        summary=project.summary,
        description=project.description,
        base_layer_dir=base_layer_dir,
    )
    image.set_environment.assert_called_once_with(project.environment)
    image.set_annotations.assert_called_once_with(annotations)
    image.set_control_data.assert_called_once_with(metadata)
    image.set_media_type.assert_called_once_with(arch="amd64")
    image.to_oci_archive.assert_called_once_with(
        tag=project.version, filename=f"{project.name}_{project.version}_test-rock.rock"
    )
