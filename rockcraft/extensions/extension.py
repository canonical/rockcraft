# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2018-2023 Canonical Ltd.
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

"""Extension base class definition."""

import abc
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, final

from craft_cli import emit

from rockcraft import errors


class Extension(abc.ABC):
    """Extension is the class from which all extensions inherit.

    Extensions have the ability to add snippets to apps, parts, and indeed add new parts
    to a given snapcraft.yaml.

    :ivar project_root: the root of the project.
    :ivar yaml_data: the raw yaml data.
    """

    def __init__(
        self,
        *,
        project_root: Path,
        yaml_data: dict[str, Any],
    ) -> None:
        """Create a new Extension."""
        self.project_root = project_root
        self.yaml_data = yaml_data

    @staticmethod
    @abc.abstractmethod
    def get_supported_bases() -> tuple[str, ...]:
        """Return a tuple of supported bases."""

    @staticmethod
    @abc.abstractmethod
    def is_experimental(base: str | None) -> bool:
        """Return whether or not this extension is unstable for given base."""

    @abc.abstractmethod
    def get_root_snippet(self) -> dict[str, Any]:
        """Return the root snippet to apply."""

    @abc.abstractmethod
    def get_part_snippet(self) -> dict[str, Any]:
        """Return the part snippet to apply to existing parts."""

    @abc.abstractmethod
    def get_parts_snippet(self) -> dict[str, Any]:
        """Return the parts to add to parts."""

    @final
    def validate(self, extension_name: str) -> None:
        """Validate that the extension can be used with the current project.

        :param extension_name: the name of the extension being parsed.
        :raises errors.ExtensionError: if the extension is incompatible with the project.
        """
        if "base" not in self.yaml_data:
            # There is nothing to validate, the extension will set the preferred base.
            return

        base: str = self.yaml_data["base"]

        if self.is_experimental(base) and not os.getenv(
            "ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS"
        ):
            raise errors.ExtensionError(
                f"Extension is experimental: {extension_name!r}",
                docs_url="https://rockcraft.io/docs/supported-extensions",
            )

        if self.is_experimental(base):
            emit.progress(
                f"*EXPERIMENTAL* extension {extension_name!r} enabled",
                permanent=True,
            )

        if base not in self.get_supported_bases():
            raise errors.ExtensionError(
                f"Extension {extension_name!r} does not support base: {base!r}"
            )

        invalid_parts = [
            p
            for p in self.get_parts_snippet()
            if not p.startswith(f"{extension_name}/")
        ]
        if invalid_parts:
            raise ValueError(
                f"Extension has invalid part names: {invalid_parts!r}. "
                "Format is <extension-name>/<part-name>"
            )


def get_extensions_data_dir() -> Path:
    """Return the path to the extension data directory."""
    return Path(sys.prefix) / "share" / "rockcraft" / "extensions"


def append_to_env(env_variable: str, paths: Sequence[str], separator: str = ":") -> str:
    """Return a string for env_variable with one of more paths appended.

    :param env_variable: the variable to operate on.
    :param paths: one or more paths to append.
    :param separator: the separator to use.
    :returns: a shell string where one or more paths are appended
                  to env_variable. The code takes into account the case
                  where the environment variable is empty, to avoid putting
                  a separator token at the start.
    """
    return f"${{{env_variable}:+${env_variable}{separator}}}" + separator.join(paths)


def prepend_to_env(
    env_variable: str, paths: Sequence[str], separator: str = ":"
) -> str:
    """Return a string for env_variable with one of more paths prepended.

    :param env_variable: the variable to operate on.
    :param paths: one or more paths to append.
    :param separator: the separator to use.
    :returns: a shell string where one or more paths are prepended
                  before env_variable. The code takes into account the case
                  where the environment variable is empty, to avoid putting
                  a separator token at the end.
    """
    return separator.join(paths) + f"${{{env_variable}:+{separator}${env_variable}}}"
