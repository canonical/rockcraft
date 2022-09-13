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

"""Multipass build environment provider for Rockcraft."""

import contextlib
import logging
import pathlib
import sys
from typing import Generator, List

from craft_providers import Executor, bases, multipass
from craft_providers.multipass.errors import MultipassError

from rockcraft.errors import ProviderError
from rockcraft.utils import (
    confirm_with_user,
    get_managed_environment_project_path,
    get_managed_environment_snap_channel,
)

from ._provider import Provider
from .providers import BASE_TO_BUILDD_IMAGE_ALIAS

logger = logging.getLogger(__name__)


class MultipassProvider(Provider):
    """Multipass build environment provider.

    :param multipass: Optional Multipass client to use.
    """

    def __init__(
        self,
        instance: multipass.Multipass = multipass.Multipass(),
    ) -> None:
        self.multipass = instance

    def clean_project_environments(
        self, *, project_name: str, project_path: pathlib.Path
    ) -> List[str]:
        """Clean up any build environments created for project.

        :param project_name: Name of the project.
        :param project_path: Directory of the project.

        :returns: List of containers deleted.
        """
        deleted: List[str] = []

        # Nothing to do if provider is not installed.
        if not self.is_provider_available():
            return deleted

        inode = project_path.stat().st_ino

        try:
            names = self.multipass.list()
        except multipass.MultipassError as error:
            raise ProviderError(str(error)) from error

        for name in names:
            if name == f"rockcraft-{project_name}-{inode}":
                logger.debug("Deleting Multipass VM %r.", name)
                try:
                    self.multipass.delete(
                        instance_name=name,
                        purge=True,
                    )
                except multipass.MultipassError as error:
                    raise ProviderError(str(error)) from error

                deleted.append(name)
            else:
                logger.debug("Not deleting Multipass VM %r.", name)

        return deleted

    @classmethod
    def ensure_provider_is_available(cls) -> None:
        """Ensure provider is available, prompting the user to install it if required.

        :raises ProviderError: if provider is not available.
        """
        if not multipass.is_installed():
            if confirm_with_user(
                "Multipass is required, but not installed. Do you wish to install Multipass "
                "and configure it with the defaults?",
                default=False,
            ):
                try:
                    multipass.install()
                except multipass.MultipassInstallationError as error:
                    raise ProviderError(
                        "Failed to install Multipass. Visit https://multipass.run/ for "
                        "instructions on installing Multipass for your operating system.",
                    ) from error
            else:
                raise ProviderError(
                    "Multipass is required, but not installed. Visit https://multipass.run/ for "
                    "instructions on installing Multipass for your operating system.",
                )

        try:
            multipass.ensure_multipass_is_ready()
        except multipass.MultipassError as error:
            raise ProviderError(str(error)) from error

    @classmethod
    def is_provider_available(cls) -> bool:
        """Check if provider is installed and available for use.

        :returns: True if installed.
        """
        return multipass.is_installed()

    @contextlib.contextmanager
    def launched_environment(
        self,
        *,
        project_name: str,
        project_path: pathlib.Path,
        build_base: str,
    ) -> Generator[Executor, None, None]:
        """Launch environment for specified base.

        :param project_name: Name of the project.
        :param project_path: Path to project.
        :param build_base: Base to build from.
        """
        alias = BASE_TO_BUILDD_IMAGE_ALIAS[build_base]

        instance_name = self.get_instance_name(
            project_name=project_name,
            project_path=project_path,
        )

        # injecting a snap on a non-linux system is not supported, so default to
        # install rockcraft from the store's stable channel
        snap_channel = get_managed_environment_snap_channel()
        if sys.platform != "linux" and not snap_channel:
            snap_channel = "stable"

        environment = self.get_command_environment()
        base_configuration = bases.BuilddBase(
            alias=alias,
            compatibility_tag=f"rockcraft-{bases.BuilddBase.compatibility_tag}.0",
            environment=environment,
            hostname=instance_name,
            snaps=[
                bases.buildd.Snap(
                    name="rockcraft",
                    channel=snap_channel,
                    classic=True,
                )
            ],
        )

        try:
            instance = multipass.launch(
                name=instance_name,
                base_configuration=base_configuration,
                # XXX: replace with appropriate rockcraft base image
                image_name=f"snapcraft:{build_base.replace(':', '-')}",
                cpus=2,
                disk_gb=64,
                mem_gb=2,
                auto_clean=True,
            )
        except (bases.BaseConfigurationError, MultipassError) as error:
            raise ProviderError(str(error)) from error

        try:
            # Mount project.
            instance.mount(
                host_source=project_path, target=get_managed_environment_project_path()
            )
        except MultipassError as error:
            raise ProviderError(str(error)) from error

        try:
            yield instance
        finally:
            # Ensure to unmount everything and stop instance upon completion.
            try:
                instance.unmount_all()
                instance.stop()
            except MultipassError as error:
                raise ProviderError(str(error)) from error
