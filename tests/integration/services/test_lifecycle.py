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
import os
from pathlib import Path

import pytest
from craft_parts import overlays

from rockcraft.services import lifecycle
from tests.testing.project import create_project
from tests.util import jammy_only

pytestmark = [jammy_only, pytest.mark.usefixtures("reset_callbacks")]

# pyright: reportPrivateImportUsage=false


def test_package_repositories_in_overlay(new_dir, mocker, run_lifecycle):
    # Mock overlay-related calls that need root; we won't be actually installing
    # any packages, just checking that the repositories are correctly installed
    # in the overlay.
    mocker.patch.object(overlays.OverlayManager, "refresh_packages_list")
    mocker.patch.object(overlays.OverlayManager, "download_packages")
    mocker.patch.object(overlays.OverlayManager, "install_packages")
    mocker.patch.object(os, "geteuid", return_value=0)

    parts = {
        "with-overlay": {
            "plugin": "nil",
            "overlay-packages": ["hello"],
        }
    }
    work_dir = Path("work")

    base_layer_dir = Path(new_dir) / "base"
    base_layer_dir.mkdir()

    # Create a fake Apt installation inside the base layer dir
    (base_layer_dir / "etc/apt").mkdir(parents=True)
    (base_layer_dir / "etc/apt/keyrings").mkdir()
    (base_layer_dir / "etc/apt/sources.list.d").mkdir()
    (base_layer_dir / "etc/apt/preferences.d").mkdir()

    package_repositories = [
        {"type": "apt", "ppa": "mozillateam/ppa", "priority": "always"}
    ]

    # Mock the installation of package repositories in the base system, as that
    # is undesired and will fail without root.
    mocker.patch.object(lifecycle, "_install_package_repositories")

    project = create_project(
        base="ubuntu:22.04",
        parts=parts,
        package_repositories=package_repositories,
    )
    lifecycle_service = run_lifecycle(
        project=project,
        work_dir=work_dir,
        base_layer_dir=base_layer_dir,
    )
    parts_lifecycle = lifecycle_service._lcm

    overlay_apt = parts_lifecycle.project_info.overlay_dir / "packages/etc/apt"
    assert overlay_apt.is_dir()

    # Checking that the files are present should be enough
    assert (overlay_apt / "keyrings/craft-CE49EC21.gpg").is_file()
    assert (overlay_apt / "sources.list.d/craft-ppa-mozillateam_ppa.sources").is_file()
    assert (overlay_apt / "preferences.d/craft-archives").is_file()
