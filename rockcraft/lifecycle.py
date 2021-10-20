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

from . import oci, ui
from .parts import PartsLifecycle, Step


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
        raise CraftError("Project name not specified.")

    tag = yaml_data.get("tag")
    if not name:
        raise CraftError("Project tag not specified.")

    base = yaml_data.get("base")
    if not base:
        raise CraftError("Base not specified.")

    parts_data = yaml_data.get("parts")
    if not parts_data:
        raise CraftError("No parts specified.")

    work_dir = Path("build").absolute()
    image_dir = work_dir / "images"
    bundle_dir = work_dir / "bundles"

    # Obtain base image and extract it to use as our overlay base
    # TODO: check if image was already downloaded, etc.
    ui.emit.progress(f"Retrieving base {base}")
    base_image = oci.Image.from_docker_registry(base, image_dir=image_dir)
    ui.emit.message(f"Retrieved base {base}")

    ui.emit.progress(f"Extracting {base_image.image_name}")
    rootfs = base_image.extract_to(bundle_dir)
    ui.emit.message(f"Extracted {base_image.image_name}")

    # TODO: check if destination image already exists, etc.
    project_image = base_image.copy_to(f"{name}:rockcraft-base", image_dir=image_dir)

    lifecycle = PartsLifecycle(
        parts_data,
        work_dir=work_dir,
        base_layer_dir=rootfs,
        base_layer_hash=project_image.digest(),
    )
    lifecycle.run(Step.PRIME)

    ui.emit.progress("Creating new layer")
    project_image.add_layer(tag, lifecycle.prime_dir)
    ui.emit.message("Created new layer")

    ui.emit.progress("Exporting to OCI archive")
    project_image.to_oci_archive(tag)
    ui.emit.progress(f"Exported to OCI archive '{name}-{tag}.oci.tar'")
