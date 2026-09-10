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
from typing import Any, cast, final

from craft_application._const import BASES_ALLOW_SLASH_IN_PART_NAME
from craft_cli import emit

from rockcraft import errors


def get_project_base(yaml_data: dict[str, Any]) -> str | None:
    """Extract and normalize the effective base used in the project.

    ``build-base`` takes precedence over ``base``. When ``base`` is ``bare`` the
    ``build-base`` is mandatory, so it always resolves the effective Ubuntu series.
    """
    base_str = cast(str | None, yaml_data.get("build-base") or yaml_data.get("base"))

    if not base_str:
        return None

    # Support the deprecated "<base>:<series>" colon format as an alias for "<base>@<series>"
    if base_str.count(":") == 1 and "@" not in base_str:
        base_str = base_str.replace(":", "@")

    # "devel" is a valid build-base that corresponds to "ubuntu@devel".
    if base_str == "devel":
        return "ubuntu@devel"

    if base_str.count("@") != 1:
        return None

    return base_str


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
        extension_name: str,
    ) -> None:
        """Create a new Extension."""
        self.project_root = project_root
        self.yaml_data = yaml_data
        self.extension_name = extension_name

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

    @property
    def _extension_name_sep(self) -> str:
        """Return the string separating extension part name fragments."""
        base = get_project_base(self.yaml_data)
        return "/" if base in BASES_ALLOW_SLASH_IN_PART_NAME else "."

    def get_part_name(self, part: str) -> str:
        """Return formatted internal part name."""
        return f"{self.extension_name}{self._extension_name_sep}{part}"

    @final
    def validate(self) -> None:
        """Validate that the extension can be used with the current project.

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
                f"Extension is experimental: {self.extension_name!r}",
                doc_slug="/reference/extensions/",
                resolution="Run with ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=True to enable "
                "experimental extensions.",
            )

        if self.is_experimental(base):
            emit.progress(
                f"*EXPERIMENTAL* extension {self.extension_name!r} enabled",
                permanent=True,
            )

        if base not in self.get_supported_bases():
            raise errors.ExtensionError(
                f"Extension {self.extension_name!r} does not support base: {base!r}"
            )

        invalid_parts = [
            p
            for p in self.get_parts_snippet()
            if not p.startswith(f"{self.extension_name}{self._extension_name_sep}")
        ]
        if invalid_parts:
            raise ValueError(
                f"Extension has invalid part names: {invalid_parts!r}. "
                f"Format is <extension-name>{self._extension_name_sep}<part-name>"
            )


class _FrameworkFactory:
    """Route to V1 or V2 extension based on project base."""

    def __init__(self, v1_cls: type[Extension], v2_cls: type[Extension]) -> None:
        self._v1_cls = v1_cls
        self._v2_cls = v2_cls

    def __call__(
        self, *, project_root: Path, yaml_data: dict[str, Any], extension_name: str
    ) -> Extension:
        base = get_project_base(yaml_data)
        if base in self._v1_cls.get_supported_bases():
            return self._v1_cls(
                project_root=project_root,
                yaml_data=yaml_data,
                extension_name=extension_name,
            )
        return self._v2_cls(
            project_root=project_root,
            yaml_data=yaml_data,
            extension_name=extension_name,
        )

    def get_supported_bases(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                self._v1_cls.get_supported_bases() + self._v2_cls.get_supported_bases()
            )
        )

    def is_experimental(self, base: str | None) -> bool:
        if base in self._v1_cls.get_supported_bases():
            return self._v1_cls.is_experimental(base)
        return self._v2_cls.is_experimental(base)


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
