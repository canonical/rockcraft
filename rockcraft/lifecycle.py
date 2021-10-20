#!/usr/bin/env python3
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


"""Lifecycle integration."""

from pathlib import Path

import yaml
from craft_cli.errors import CraftError

from . import oci
from .parts import PartsLifecycle, Step
from .ui import emit


def pack():
    """Pack a ROCK."""
    # XXX: replace with proper rockcraft.yaml unmarshal and validation
    try:
        with open("rockcraft.yaml", encoding="utf-8") as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
    except OSError as err:
        raise CraftError(err) from err

    name = yaml_data.get("name")
    if not name:
        emit.message("Project name not specified.")
        return

    tag = yaml_data.get("tag")
    if not name:
        emit.message("Project tag not specified.")
        return

    base = yaml_data.get("base")
    if not base:
        emit.message("Base not specified.")
        return

    parts_data = yaml_data.get("parts")
    if not parts_data:
        emit.message("No parts specified.")
        return

    work_dir = Path("build").absolute()
    image_dir = work_dir / "images"
    bundle_dir = work_dir / "bundles"

    # Obtain base image and extract it to use as our overlay base
    # TODO: check if image was already downloaded, etc.
    base_image = oci.Image.from_docker_registry(base, image_dir=image_dir)
    rootfs = base_image.extract_to(bundle_dir)

    # TODO: check if destination image already exists, etc.
    project_image = base_image.copy_to(f"{name}:rockcraft-base", image_dir=image_dir)

    lifecycle = PartsLifecycle(
        parts_data,
        work_dir=work_dir,
        base_layer_dir=rootfs,
        base_layer_hash=project_image.digest(),
    )
    lifecycle.run(Step.PRIME)

    project_image.add_layer(tag, lifecycle.prime_dir)

    project_image.to_oci_archive(tag)
