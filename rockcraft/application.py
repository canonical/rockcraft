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

from pathlib import Path
from typing import Any

from craft_application import Application, AppMetadata
from craft_parts.plugins.plugins import PluginType
from overrides import override  # type: ignore[reportUnknownVariableType]

from rockcraft import models, plugins
from rockcraft.models import project

APP_METADATA = AppMetadata(
    name="rockcraft",
    summary="A tool to create OCI images",
    ProjectClass=project.Project,
    BuildPlannerClass=project.BuildPlanner,
    source_ignore_patterns=["*.rock"],
    docs_url="https://documentation.ubuntu.com/rockcraft/en/stable",
)


class Rockcraft(Application):
    """Rockcraft application definition."""

    @override
    def _extra_yaml_transform(
        self,
        yaml_data: dict[str, Any],
        *,
        build_on: str,
        build_for: str | None,
    ) -> dict[str, Any]:
        return models.transform_yaml(Path.cwd(), yaml_data)

    @override
    def _configure_services(self, provider_name: str | None) -> None:
        self.services.set_kwargs(
            "image",
            work_dir=self._work_dir,
            build_plan=self._build_plan,
        )
        self.services.set_kwargs(
            "package",
            build_plan=self._build_plan,
        )
        super()._configure_services(provider_name)

    @override
    def _get_app_plugins(self) -> dict[str, PluginType]:
        """Get the plugins for this application.

        Should be overridden by applications that need to register plugins at startup.
        """
        return plugins.get_plugins()

    @override
    def _enable_craft_parts_features(self) -> None:
        # pylint: disable=import-outside-toplevel
        from craft_parts.features import Features

        # enable the craft-parts Features that we use here, right before
        # loading the project and validating its parts.
        Features(enable_overlay=True)
