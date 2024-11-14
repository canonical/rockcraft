#  This file is part of Rockcraft.
#
#  Copyright 2023 Canonical Ltd.
#
#  This program is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License version 3, as
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
#  SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Project-related utility functions for running lifecycles."""

import pathlib
from typing import cast

from craft_application import models
from rockcraft.application import APP_METADATA
from rockcraft.models import Project
from rockcraft.services import RockcraftLifecycleService, RockcraftServiceFactory
from rockcraft.services.image import ImageInfo


def run_mocked_lifecycle(
    *,
    project: Project,
    work_dir: pathlib.Path,
    mocker,
    base_layer_dir: pathlib.Path | None = None,
    step: str = "stage",
    build_plan: list[models.BuildInfo]
) -> RockcraftLifecycleService:
    """Run a project's lifecycle with a mocked base image."""

    factory = RockcraftServiceFactory(APP_METADATA)
    factory.update_kwargs(
        "lifecycle",
        work_dir=work_dir,
        cache_dir=work_dir / "cache_dir",
        build_plan=build_plan,
    )
    factory.update_kwargs(
        "image",
        work_dir=work_dir,
        build_plan=build_plan,
    )
    factory.project = project

    image_info = ImageInfo(
        base_image=mocker.MagicMock(),
        base_layer_dir=base_layer_dir or pathlib.Path("unused"),
        base_digest=b"deadbeef",
    )
    mocker.patch.object(factory.image, "obtain_image", return_value=image_info)

    lifecycle_service = factory.lifecycle
    lifecycle_service.run(step)

    return cast(RockcraftLifecycleService, lifecycle_service)
