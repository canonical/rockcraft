# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021 Canonical Ltd.
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

"""Build environment provider support for rockcraft."""

import contextlib
import pathlib
from abc import ABC, abstractmethod
from typing import Generator, List, Tuple, Union

from craft_providers import Executor


class Provider(ABC):
    """Rockcraft's build environment provider."""

    @abstractmethod
    def clean_project_environments(
        self, *, project_name: str, project_path: pathlib.Path
    ) -> List[str]:
        """Clean up any environments created for project.

        :param project_name: Name of project.

        :returns: List of containers deleted.
        """

    @classmethod
    @abstractmethod
    def ensure_provider_is_available(cls) -> None:
        """Ensure provider is available, prompting the user to install it if required.

        :raises ProviderError: if provider is not available.
        """

    @classmethod
    def is_base_available(cls, base: str) -> Tuple[bool, Union[str, None]]:
        """Check if provider can provide an environment matching given base.

        :param base: Base to check.

        :returns: Tuple of bool indicating whether it is a match, with optional
                reason if not a match.
        """
        if base not in ["ubuntu:18.04", "ubuntu:20.04"]:
            return (
                False,
                f"Base {base!r} is not supported (must be 'ubuntu:18.04' or 'ubuntu:20.04')",
            )

        return True, None

    @classmethod
    @abstractmethod
    def is_provider_available(cls) -> bool:
        """Check if provider is installed and available for use.

        :returns: True if installed.
        """

    # TODO: migrate `create_environment()` from snapcraft or charmcraft

    @abstractmethod
    @contextlib.contextmanager
    def launched_environment(
        self,
        *,
        project_name: str,
        project_path: pathlib.Path,
        build_base: str,
        instance_name: str,
    ) -> Generator[Executor, None, None]:
        """Configure and launch environment for specified base.

        When this method loses context, all directories are unmounted and the
        environment is stopped. For more control of environment setup and teardown,
        use `create_environment()` instead.

        :param project_name: Name of project.
        :param project_path: Path to project.
        :param build_base: Base to build from.
        :param instance_name: Name of the instance to launch.
        """
