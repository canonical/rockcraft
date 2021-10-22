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
from .project import Project


def pack():
    """Pack a ROCK."""
    # XXX: replace with proper rockcraft.yaml unmarshal and validation
    try:
        with open("rockcraft.yaml", encoding="utf-8") as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
    except OSError as err:
        raise CraftError(err) from err

    project = Project.unmarshal(yaml_data)

    work_dir = Path("work").absolute()
    image_dir = work_dir / "images"
    bundle_dir = work_dir / "bundles"

    # Obtain base image and extract it to use as our overlay base
    # TODO: check if image was already downloaded, etc.
    ui.emit.progress(f"Retrieving base {project.base}")
    base_image = oci.Image.from_docker_registry(project.base, image_dir=image_dir)
    ui.emit.message(f"Retrieved base {project.base}")

    ui.emit.progress(f"Extracting {base_image.image_name}")
    rootfs = base_image.extract_to(bundle_dir)
    ui.emit.message(f"Extracted {base_image.image_name}")

    # TODO: check if destination image already exists, etc.
    project_image = base_image.copy_to(
        f"{project.name}:rockcraft-base", image_dir=image_dir
    )

    lifecycle = PartsLifecycle(
        project.parts,
        work_dir=work_dir,
        base_layer_dir=rootfs,
        base_layer_hash=project_image.digest(),
    )
    lifecycle.run(Step.PRIME)

    ui.emit.progress("Creating new layer")
    project_image.add_layer(tag=project.version, layer_path=lifecycle.prime_dir)
    ui.emit.message("Created new layer")

    ui.emit.progress("Exporting to OCI archive")
    archive_name = f"{project.name}-{project.version}.rock"
    project_image.to_oci_archive(tag=project.version, filename=archive_name)
    ui.emit.progress(f"Exported to OCI archive '{archive_name}'")
