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

"""Main Rockcraft Application."""

from __future__ import annotations

import functools
import pathlib

import craft_cli
from craft_application import Application, AppMetadata, util
from overrides import override

from rockcraft import models
from rockcraft.models import project

APP_METADATA = AppMetadata(
    name="rockcraft",
    summary="A tool to create OCI images",
    ProjectClass=project.Project,
    source_ignore_patterns=["*.rock"],
)


class Rockcraft(Application):
    """Rockcraft application definition."""

    @functools.cached_property
    def project(self) -> models.Project:
        """Get this application's Project metadata."""
        project_file = (pathlib.Path.cwd() / f"{self.app.name}.yaml").resolve()
        craft_cli.emit.debug(f"Loading project file '{project_file!s}'")
        return models.Project.from_yaml_file(project_file, work_dir=self._work_dir)

    @override
    def _configure_services(self, platform: str | None, build_for: str | None) -> None:
        if build_for is None:
            build_for = util.get_host_architecture()

        self.services.set_kwargs("image", work_dir=self._work_dir, build_for=build_for)
        self.services.set_kwargs(
            "package",
            platform=platform,
            build_for=build_for,
        )
        super()._configure_services(platform, build_for)
