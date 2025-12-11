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
import sys
from pathlib import Path

import pytest
import yaml
from rockcraft import cli
from rockcraft.services.image import ImageInfo, RockcraftImageService

from tests.util import jammy_only

pytestmark = [jammy_only]


# A Rockcraft project whose build step writes some global CRAFT_* variables to
# a yaml file.
ROCKCRAFT_YAML = """\
name: my-project
title: My Project
version: 1.2.3
base: bare
build-base: "ubuntu@22.04"
summary: "example of global variables"
description: "example of global variables"
license: Apache-2.0

platforms:
    amd64:
    arm64:

parts:
    foo:
        plugin: nil
        override-build: |
            target_file=${CRAFT_PART_INSTALL}/variables.yaml
            touch $target_file
            echo "project_name:    \\"${CRAFT_PROJECT_NAME}\\""    >> $target_file
            echo "project_dir:     \\"${CRAFT_PROJECT_DIR}\\""     >> $target_file
            echo "project_version: \\"${CRAFT_PROJECT_VERSION}\\"" >> $target_file
"""


@pytest.mark.slow
def test_global_environment(
    new_dir,
    monkeypatch,
    mocker,
):
    """Test our additions to the global environment that is available to the
    build process."""

    rootfs = Path(new_dir) / "rootfs"
    rootfs.mkdir()
    fake_digest = b"deadbeef"

    image_info = ImageInfo(
        base_image=mocker.MagicMock(), base_layer_dir=rootfs, base_digest=fake_digest
    )
    mocker.patch.object(RockcraftImageService, "obtain_image", return_value=image_info)

    Path("rockcraft.yaml").write_text(ROCKCRAFT_YAML)

    monkeypatch.setattr(sys, "argv", ["rockcraft", "prime", "--destructive-mode"])

    app = cli._create_app()
    app.run()

    variables_yaml = Path(new_dir) / "stage/variables.yaml"
    assert variables_yaml.is_file()
    variables = yaml.safe_load(variables_yaml.read_text())

    assert variables["project_name"] == "my-project"
    assert variables["project_dir"] == str(new_dir)
    assert variables["project_version"] == "1.2.3"
