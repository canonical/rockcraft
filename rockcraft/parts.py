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
from typing import Any, Dict

import craft_parts
from craft_cli.errors import CraftError
from craft_parts import ActionType, Step
from xdg import BaseDirectory  # type: ignore

from rockcraft import ui


class PartsLifecycleError(CraftError):
    """Error during parts processing."""


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
        base_layer_dir: pathlib.Path,
        base_layer_hash: bytes,
    ):
        ui.emit.progress("Initializing parts lifecycle")

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
            )
        except craft_parts.PartsError as err:
            raise PartsLifecycleError(err) from err

    @property
    def prime_dir(self) -> pathlib.Path:
        """Return the parts prime directory path."""
        return self._lcm.project_info.prime_dir

    def run(self, target_step: Step) -> None:
        """Run the parts lifecycle.

        :param target_step: The final step to execute.

        :raises PartsLifecycleError: On error during lifecycle.
        :raises RuntimeError: On unexpected error.
        """
        try:
            ui.emit.progress("Executing parts lifecycle")

            actions = self._lcm.plan(target_step)
            with self._lcm.action_executor() as aex:
                for action in actions:
                    message = _action_message(action)
                    ui.emit.progress(f"Run parts lifecycle: {message}")
                    aex.execute(action)

            ui.emit.message("Executed parts lifecycle")
        except RuntimeError as err:
            raise RuntimeError(f"Parts processing internal error: {err}") from err
        except OSError as err:
            msg = err.strerror
            if err.filename:
                msg = f"{err.filename}: {msg}"
            raise PartsLifecycleError(msg) from err
        except Exception as err:
            raise PartsLifecycleError(err) from err


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
