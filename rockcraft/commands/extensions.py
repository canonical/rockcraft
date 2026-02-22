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

"""Extension-related cli commands."""

import abc
import argparse
import textwrap

import tabulate
from craft_application.commands import AppCommand
from craft_cli import emit
from overrides import overrides  # type: ignore[reportUnknownVariableType]
from pydantic import BaseModel

from rockcraft import extensions
from rockcraft.models import Project


class ExtensionModel(BaseModel):
    """Extension model for presentation."""

    name: str
    bases: list[str]

    def marshal(self) -> dict[str, str]:
        """Marshal model into a dictionary for presentation."""
        return {
            "Extension name": self.name,
            "Supported bases": ", ".join(sorted(self.bases)),
        }


class ListExtensionsCommand(AppCommand, abc.ABC):
    """List available extensions for all supported bases."""

    name = "list-extensions"
    help_msg = "List available extensions for all supported bases."
    overview = textwrap.dedent(
        """
        List available extensions and their corresponding bases.
        """
    )

    @overrides
    def run(self, parsed_args: argparse.Namespace) -> None:  # noqa: ARG002 (unused arg)
        """Print the list of available extensions and their bases."""
        extension_presentation: dict[str, ExtensionModel] = {}

        for extension_name in extensions.registry.get_extension_names():
            extension_class = extensions.registry.get_extension_class(extension_name)
            extension_bases = list(extension_class.get_supported_bases())
            extension_presentation[extension_name] = ExtensionModel(
                name=extension_name, bases=extension_bases
            )

        printable_extensions = sorted(
            [v.marshal() for v in extension_presentation.values()],
            key=lambda d: d["Extension name"],
        )
        emit.message(tabulate.tabulate(printable_extensions, headers="keys"))


class ExtensionsCommand(ListExtensionsCommand, abc.ABC):
    """A command alias to list the available extensions."""

    name = "extensions"
    hidden = True


class ExpandExtensionsCommand(AppCommand, abc.ABC):
    """Expand the extensions in the rockcraft.yaml file."""

    name = "expand-extensions"
    help_msg = "Expand extensions in rockcraft.yaml"
    overview = textwrap.dedent(
        """
        Extensions listed in rockcraft.yaml will be
        expanded and shown as output.
        """
    )

    @overrides
    def run(self, parsed_args: argparse.Namespace) -> None:  # noqa: ARG002 (unused arg)
        """Print the project's specification with the extensions expanded."""
        project_service = self._services.get("project")
        raw_project = project_service.get_raw()
        project_path = project_service.resolve_project_file_path()

        processed_data = extensions.apply_extensions(
            project_root=project_path.parent, yaml_data=raw_project
        )
        project = Project.from_yaml_data(processed_data, project_path)

        emit.message(project.to_yaml_string())
