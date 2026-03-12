# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2024 Canonical Ltd.
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

"""Rockcraft Init Service."""

import pathlib
from typing import Any

from craft_application.services import InitService
from craft_cli import emit
from overrides import override  # type: ignore[reportUnknownVariableType]


class RockcraftInitService(InitService):
    """Rockcraft specialization of the InitService."""

    @override
    def initialise_project(
        self,
        *,
        project_dir: pathlib.Path,
        project_name: str,
        template_dir: pathlib.Path,
    ) -> None:
        super().initialise_project(
            project_dir=project_dir,
            project_name=project_name,
            template_dir=template_dir,
        )

        init_profile = template_dir.name
        if init_profile not in ("simple", "test"):
            versioned_docs = self._app.versioned_docs_url
            reference_docs = f"{versioned_docs}/reference/extensions/{init_profile}"
            emit.message(
                f"Go to {reference_docs} to read more about the "
                f"{init_profile!r} profile."
            )

    @override
    def _get_context(self, name: str, *, project_dir: pathlib.Path) -> dict[str, Any]:
        context = super()._get_context(name, project_dir=project_dir)
        context["snake_name"] = context["name"].replace("-", "_").lower()
        context["versioned_url"] = self._app.versioned_docs_url

        return context
