# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2021 Canonical Ltd.
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

"""Craft-parts lifecycle."""

import pathlib
import subprocess
from typing import Any, Dict, List, Optional

import craft_parts
from craft_archives import repo
from craft_cli import emit
from craft_parts import ActionType, Step
from xdg import BaseDirectory  # type: ignore

from rockcraft.errors import PartsLifecycleError

_LIFECYCLE_STEPS = {
    "pull": Step.PULL,
    "overlay": Step.OVERLAY,
    "build": Step.BUILD,
    "stage": Step.STAGE,
    "prime": Step.PRIME,
}


craft_parts.Features(enable_overlay=True)


class PartsLifecycle:
    """Create and manage the parts lifecycle.

    :param all_parts: A dictionary containing the parts defined in the project.
    :param work_dir: The working directory for parts processing.
    :param base_layer_dir: The path to the extracted base root filesystem.
    :param base_layer_hash: The base image digest.

    :raises PartsLifecycleError: On error initializing the parts lifecycle.
    """

    def __init__(
        self,
        all_parts: Dict[str, Any],
        *,
        work_dir: pathlib.Path,
        part_names: Optional[List[str]],
        base_layer_dir: pathlib.Path,
        base_layer_hash: bytes,
        base: str,
        package_repositories: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self._part_names = part_names
        self._package_repositories = package_repositories or []

        emit.progress("Initializing parts lifecycle")

        # set the cache dir for parts package management
        cache_dir = BaseDirectory.save_cache_path("rockcraft")

        try:
            self._lcm = craft_parts.LifecycleManager(
                {"parts": all_parts},
                application_name="rockcraft",
                work_dir=work_dir,
                cache_dir=cache_dir,
                base_layer_dir=base_layer_dir,
                base_layer_hash=base_layer_hash,
                ignore_local_sources=["*.rock"],
                base=base,
            )
        except craft_parts.PartsError as err:
            raise PartsLifecycleError.from_parts_error(err) from err

    def clean(self) -> None:
        """Remove lifecycle artifacts."""
        if self._part_names:
            message = "Cleaning parts: " + ", ".join(self._part_names)
        else:
            message = "Cleaning all parts"

        emit.progress(message)
        self._lcm.clean(part_names=self._part_names)

    @property
    def prime_dir(self) -> pathlib.Path:
        """Return the parts prime directory path."""
        return self._lcm.project_info.prime_dir

    def run(  # noqa PLR0912,PLR0915  Copied from pylint directive below but for ruff
        self,
        step_name: str,
        *,
        shell: bool = False,
        shell_after: bool = False,
        debug: bool = False,
    ) -> None:
        """Run the parts lifecycle.

        :param step_name: The final step to execute.
        :param shell: Execute a shell instead of the target step.
        :param shell_after: Execute a shell after the target step.
        :param debug: Execute a shell on failure.

        :raises PartsLifecycleError: On error during lifecycle.
        :raises RuntimeError: On unexpected error.
        """
        # pylint: disable=too-many-branches,too-many-statements
        target_step = _LIFECYCLE_STEPS.get(step_name)
        if not target_step:
            raise RuntimeError(f"Invalid target step {step_name!r}")

        if shell:
            # convert shell to shell_after for the previous step
            previous_steps = target_step.previous_steps()
            target_step = previous_steps[-1] if previous_steps else None
            shell_after = True

        try:
            if target_step:
                actions = self._lcm.plan(target_step, part_names=self._part_names)
            else:
                actions = []

            if self._package_repositories:
                emit.progress("Installing package repositories")
                self._install_package_repositories()

            emit.progress("Executing parts lifecycle")

            with self._lcm.action_executor() as aex:
                for action in actions:
                    message = _action_message(action)
                    emit.progress(f"Executing parts lifecycle: {message}")
                    with emit.open_stream("Executing action") as stream:
                        aex.execute(action, stdout=stream, stderr=stream)
                    emit.progress(f"Executed: {message}", permanent=True)

            if shell_after:
                launch_shell()

            emit.progress("Executed parts lifecycle", permanent=True)
        except craft_parts.PartsError as err:
            if debug:
                emit.progress(str(err), permanent=True)
                launch_shell()
            raise PartsLifecycleError.from_parts_error(err) from err
        except RuntimeError as err:
            if debug:
                emit.progress(str(err), permanent=True)
                launch_shell()
            raise RuntimeError(f"Parts processing internal error: {err}") from err
        except OSError as err:
            msg = err.strerror
            if err.filename:
                msg = f"{err.filename}: {msg}"
            if debug:
                emit.progress(msg, permanent=True)
                launch_shell()
            raise PartsLifecycleError(msg) from err
        except Exception as err:  # noqa BLE001 - this is an error conversion.
            if debug:
                emit.progress(str(err), permanent=True)
                launch_shell()
            raise PartsLifecycleError(str(err)) from err

    def _install_package_repositories(self) -> None:
        """Install package repositories in the environment."""
        if not self._package_repositories:
            emit.debug("No package repositories specified, none to install.")
            return

        refresh_required = repo.install(
            self._package_repositories, key_assets=pathlib.Path("/dev/null")
        )
        if refresh_required:
            emit.progress("Refreshing repositories")
            self._lcm.refresh_packages_list()

        emit.progress("Package repositories installed", permanent=True)


def launch_shell(*, cwd: Optional[pathlib.Path] = None) -> None:
    """Launch a user shell for debugging environment.

    :param cwd: Working directory to start user in.
    """
    emit.progress("Launching shell on build environment...", permanent=True)
    with emit.pause():
        subprocess.run(["bash"], check=False, cwd=cwd)


def _action_message(action: craft_parts.Action) -> str:
    msg = {
        Step.PULL: {
            ActionType.RUN: "pull",
            ActionType.RERUN: "repull",
            ActionType.SKIP: "skip pull",
            ActionType.UPDATE: "update sources for",
        },
        Step.OVERLAY: {
            ActionType.RUN: "overlay",
            ActionType.RERUN: "re-overlay",
            ActionType.SKIP: "skip overlay",
            ActionType.UPDATE: "update overlay for",
            ActionType.REAPPLY: "reapply",
        },
        Step.BUILD: {
            ActionType.RUN: "build",
            ActionType.RERUN: "rebuild",
            ActionType.SKIP: "skip build",
            ActionType.UPDATE: "update build for",
        },
        Step.STAGE: {
            ActionType.RUN: "stage",
            ActionType.RERUN: "restage",
            ActionType.SKIP: "skip stage",
        },
        Step.PRIME: {
            ActionType.RUN: "prime",
            ActionType.RERUN: "re-prime",
            ActionType.SKIP: "skip prime",
        },
    }

    message = f"{msg[action.step][action.action_type]} {action.part_name}"

    if action.reason:
        message += f" ({action.reason})"

    return message


def validate_part(data: Dict[str, Any]) -> None:
    """Validate the given part data against common and plugin models.

    :param data: The part data to validate.
    """
    craft_parts.validate_part(data)
