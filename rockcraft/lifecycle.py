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

import subprocess
from pathlib import Path

from . import oci, providers, ui, utils
from .parts import PartsLifecycle, Step
from .project import Project, load_project
from .providers import capture_logs_from_instance


def pack():
    """Pack a ROCK."""
    project = load_project("rockcraft.yaml")

    destructive_mode = False  # XXX: obtain from command line

    managed_mode = utils.is_managed_mode()
    if not managed_mode and not destructive_mode:
        pack_in_provider(project)
        return

    if managed_mode:
        work_dir = utils.get_managed_environment_home_path()
    else:
        work_dir = Path("work").absolute()

    image_dir = work_dir / "images"
    bundle_dir = work_dir / "bundles"

    # Obtain base image and extract it to use as our overlay base
    # TODO: check if image was already downloaded, etc.
    ui.emit.progress(f"Retrieving base {project.base}")
    base_image = oci.Image.from_docker_registry(project.base, image_dir=image_dir)
    ui.emit.message(f"Retrieved base {project.base}", intermediate=True)

    ui.emit.progress(f"Extracting {base_image.image_name}")
    rootfs = base_image.extract_to(bundle_dir)
    ui.emit.message(f"Extracted {base_image.image_name}", intermediate=True)

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
    ui.emit.message("Created new layer", intermediate=True)

    ui.emit.progress("Exporting to OCI archive")
    archive_name = f"{project.name}_{project.version}.rock"
    project_image.to_oci_archive(tag=project.version, filename=archive_name)
    ui.emit.message(f"Exported to OCI archive '{archive_name}'", intermediate=True)


def pack_in_provider(project: Project):
    """Pack image in provider instance."""
    provider = providers.get_provider()
    provider.ensure_provider_is_available()

    cmd = ["rockcraft", "pack"]

    # TODO: append appropriate command line arguments

    output_dir = utils.get_managed_environment_project_path()

    ui.emit.progress("Launching instance...")
    with provider.launched_environment(
        project_name=project.name,
        project_path=Path().absolute(),
        base=project.base,
    ) as instance:
        try:
            with ui.emit.pause():
                instance.execute_run(cmd, check=True, cwd=output_dir)
            capture_logs_from_instance(instance)
        except subprocess.CalledProcessError as err:
            capture_logs_from_instance(instance)
            raise providers.ProviderError(
                f"Failed to pack image '{project.name}:{project.version}'."
            ) from err
