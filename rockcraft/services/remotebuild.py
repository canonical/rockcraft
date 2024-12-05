# Copyright 2024 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For further info, check https://github.com/canonical/charmcraft
"""Charmcraft-specific overrides for the remote build service."""

import datetime
import pathlib
from collections.abc import Mapping
from typing import Any

import lazr.restfulclient.errors  # type: ignore[import-untyped]
from craft_application import launchpad
from craft_application.services import remotebuild
from overrides import override


class RemoteBuildService(remotebuild.RemoteBuildService):
    """Charmcraft remote build service."""

    RecipeClass = launchpad.models.CharmRecipe

    def fetch_logs(self, output_dir: pathlib.Path) -> Mapping[str, pathlib.Path | None]:
        """Fetch the logs for each build to the given directory.

        :param output_dir: The directory into which to place the logs.
        :returns: A mapping of the architecture to its build log.
        """
        if not self._is_setup:
            raise RuntimeError(
                "RemoteBuildService must be set up using start_builds or resume_builds before fetching logs."
            )
        project_name = self._name.split("-", maxsplit=2)[1]
        logs: dict[str, pathlib.Path | None] = {}
        log_downloads: dict[str, pathlib.Path] = {}
        fetch_time = datetime.datetime.now().isoformat(timespec="seconds")
        for build in self._builds:
            url = build.build_log_url
            if not url:
                logs[build.arch_tag] = None
                continue
            filename = f"{project_name}_{build.distribution.name}-{build.distro_series.version}-{build.arch_tag}-{fetch_time}.txt"
            logs[build.arch_tag] = output_dir / filename
            log_downloads[url] = output_dir / filename
        self.request.download_files_with_progress(log_downloads)
        return logs

    @override
    def _new_recipe(
        self,
        name: str,
        repository: launchpad.models.GitRepository,
        **_: Any,  # noqa: ANN401
    ) -> launchpad.models.Recipe:
        """Create a new recipe."""
        try:
            return launchpad.models.CharmRecipe.new(
                self.lp,
                name,
                self.lp.username,
                project=self._lp_project.name,
                git_ref=repository.self_link + "/+ref/main",
            )
        except lazr.restfulclient.errors.BadRequest:
            return self.lp.get_recipe(
                "CHARM",
                name=name,
                owner=self.lp.username,
                project=self._lp_project.name,
            )

    @override
    def _get_build_states(self) -> Mapping[str, launchpad.models.BuildState]:
        self._refresh_builds()
        return {
            f"{build.distribution.name}@{build.distro_series.version} ({build.arch_tag})": build.get_state()
            for build in self._builds
        }
