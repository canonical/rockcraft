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

from typing import TYPE_CHECKING

from craft_application import Application, AppMetadata
from craft_application.models import constraints
from overrides import override  # type: ignore[reportUnknownVariableType]

from rockcraft import plugins
from rockcraft.models import project

if TYPE_CHECKING:
    from craft_parts.plugins.plugins import PluginType

APP_METADATA = AppMetadata(
    name="rockcraft",
    summary="A tool to create OCI images",
    ProjectClass=project.Project,
    source_ignore_patterns=["*.rock"],
    docs_url="https://documentation.ubuntu.com/rockcraft/en/{version}",
    check_supported_base=True,
)


class Rockcraft(Application):
    """Rockcraft application definition."""

    @override
    def _configure_services(self, provider_name: str | None) -> None:
        self.services.update_kwargs(
            "image", work_dir=self._work_dir, project_dir=self.project_dir
        )
        self.services.update_kwargs(
            "init",
            default_name="my-rock-name",
            name_regex=constraints.PROJECT_NAME_COMPILED_REGEX,
            invalid_name_message=constraints.MESSAGE_INVALID_NAME,
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
