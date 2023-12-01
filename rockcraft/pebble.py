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

"""Pebble metadata and configuration helpers."""

import glob
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Literal

import pydantic
import yaml
from craft_application.errors import CraftValidationError
from craft_cli import emit


class HttpCheck(pydantic.BaseModel):
    """Lightweight schema validation for a Pebble HTTP check."""

    url: pydantic.AnyHttpUrl
    headers: dict[str, str] | None

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        extra = "forbid"


class TcpCheck(pydantic.BaseModel):
    """Lightweight schema validation for a Pebble TCP check."""

    port: int
    host: str | None

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        extra = "forbid"


class ExecCheck(pydantic.BaseModel):
    """Lightweight schema validation for a Pebble exec check."""

    command: str
    service_context: str | None
    environment: dict[str, str] | None
    user: str | None
    user_id: int | None
    group: str | None
    group_id: int | None
    working_dir: str | None

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        alias_generator: Callable[[str], str] = lambda s: s.replace(  # noqa: E731
            "_", "-"
        )
        extra = "forbid"


class Check(pydantic.BaseModel):
    """Lightweight schema validation for a Pebble checks.

    Based on
    https://github.com/canonical/pebble#layer-specification
    """

    override: Literal["merge", "replace"]
    level: Literal["alive", "ready"] | None
    period: str | None
    timeout: str | None
    threshold: int | None
    http: HttpCheck | None
    tcp: TcpCheck | None
    exec: ExecCheck | None

    @pydantic.root_validator(pre=True)
    @classmethod
    def _validates_check_type(cls, values: Mapping[str, Any]) -> Mapping[str, Any]:
        """Before validation, make sure only one of 'http', 'tcp' or 'exec' exist."""
        mutually_exclusive = ["http", "tcp", "exec"]
        check_types = list(set(mutually_exclusive) & values.keys())
        check_types.sort()

        if len(check_types) > 1:
            err = str(
                f"Multiple check types specified ({', '.join(check_types)}). "
                "Each check must have exactly one type."
            )
        elif len(check_types) < 1:
            err = str(
                f"Must specify exactly one of {', '.join(list(mutually_exclusive))} for each check."
            )
        else:
            return values

        raise CraftValidationError(err)

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        alias_generator: Callable[[str], str] = lambda s: s.replace(  # noqa: E731
            "_", "-"
        )
        extra = "forbid"


class Service(pydantic.BaseModel):
    """Lightweight schema validation for a Pebble service.

    Based on
    https://github.com/canonical/pebble#layer-specification
    """

    override: Literal["merge", "replace"]
    command: str
    summary: str | None
    description: str | None
    startup: Literal["enabled", "disabled"] | None
    after: list[str] | None
    before: list[str] | None
    requires: list[str] | None
    environment: dict[str, str] | None
    user: str | None
    user_id: int | None
    group: str | None
    group_id: int | None
    working_dir: str | None
    on_success: Literal["restart", "shutdown", "ignore"] | None
    on_failure: Literal["restart", "shutdown", "ignore"] | None
    on_check_failure: dict[str, Literal["restart", "shutdown", "ignore"]] | None
    backoff_delay: str | None
    backoff_factor: float | None
    backoff_limit: str | None
    kill_delay: str | None

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        alias_generator: Callable[[str], str] = lambda s: s.replace(  # noqa: E731
            "_", "-"
        )
        extra = "forbid"


class Pebble:
    """Handles the Pebble metadata information and setup operations."""

    PEBBLE_PATH = "var/lib/pebble/default"
    PEBBLE_LAYERS_PATH = f"{PEBBLE_PATH}/layers"
    PEBBLE_BINARY_PATH = "bin/pebble"
    PEBBLE_PART_SPEC = {
        "plugin": "nil",
        "stage-snaps": ["pebble/latest/stable"],
        "stage": [PEBBLE_BINARY_PATH],
        # We need this because "services" is Optional, but the directory must exist
        "override-prime": f"craftctl default\nmkdir -p {PEBBLE_LAYERS_PATH}",
    }

    def define_pebble_layer(
        self,
        target_dir: Path,
        ref_fs: Path,
        layer_content: dict[str, Any],
        rock_name: str,
    ) -> None:
        """Infers and defines a new Pebble layer file.

        Infers the Pebble layer filename based on the existing contents of
        ref_fs and writes the layer content into target_dir.

        :param target_dir: Path where to write the new Pebble layer file
        :param ref_fs: filesystem to use as a reference when inferring the layer name
        :param layer_content: the actual Pebble layer, in JSON
        :param rock_name: name of the rock where the layer will end up
        """
        # NOTE: the layer's filename prefix will always be "001-" when using
        # "bare" and "ubuntu" bases
        pebble_layers_path_in_base = f"{ref_fs}/{self.PEBBLE_LAYERS_PATH}"
        existing_pebble_layers = glob.glob(
            pebble_layers_path_in_base + "/[0-9][0-9][0-9]-???*.yaml"
        ) + glob.glob(pebble_layers_path_in_base + "/[0-9][0-9][0-9]-???*.yml")

        prefixes = list(map(lambda l: Path(l).name[:3], existing_pebble_layers))
        prefixes.sort()
        emit.progress(
            f"Found {len(existing_pebble_layers)} Pebble layers in the base's root filesystem"
        )

        new_layer_prefix = f"{(int(prefixes[-1]) + 1):03}" if prefixes else "001"
        new_layer_name = f"{new_layer_prefix}-{rock_name}.yaml"

        emit.progress(f"Preparing new Pebble layer file {new_layer_name}")

        tmp_pebble_layers_path = target_dir / self.PEBBLE_LAYERS_PATH
        tmp_pebble_layers_path.mkdir(parents=True)
        (target_dir / self.PEBBLE_PATH).chmod(0o777)

        tmp_new_layer = tmp_pebble_layers_path / new_layer_name
        with open(tmp_new_layer, "w", encoding="utf-8") as layer_fd:
            yaml.dump(
                layer_content,
                layer_fd,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

        tmp_new_layer.chmod(0o777)
