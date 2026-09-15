# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2026 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Rockcraft init command."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, get_args

from craft_application.commands import InitCommand as AppInitCommand
from typing_extensions import override

from rockcraft import extensions
from rockcraft.models.project import BaseT

if TYPE_CHECKING:
    import argparse
    import pathlib

    from rockcraft.services import RockcraftInitService


class InitCommand(AppInitCommand):
    """Initialise Rockcraft projects with base-aware template fallback."""

    @override
    def run(self, parsed_args: argparse.Namespace) -> None:
        init_service = cast("RockcraftInitService", self._services.init)
        init_service.requested_base = parsed_args.base
        super().run(parsed_args)

    @override
    def _get_template_dir(self, parsed_args: argparse.Namespace) -> pathlib.Path:
        base = getattr(parsed_args, "base", None)
        variant = self.parent_template_dir / f"{parsed_args.profile}__{base}"
        if (
            base
            and not variant.exists()
            and self._supports_default_template(parsed_args.profile, base)
        ):
            return self.parent_template_dir / parsed_args.profile

        return super()._get_template_dir(parsed_args)

    @staticmethod
    def _supports_default_template(profile: str, base: str) -> bool:
        if profile == "simple":
            return base != "bare" and base in get_args(BaseT)

        if profile not in extensions.get_extension_names():
            return False

        supported_bases = extensions.get_extension_class(profile).get_supported_bases()
        return base != "bare" and base in supported_bases
