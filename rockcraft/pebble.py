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
from pathlib import Path
from typing import Any, Dict, List, Literal, Mapping, Optional

import pydantic
import yaml
from craft_cli import emit

from rockcraft.errors import ProjectValidationError


class HttpCheck(pydantic.BaseModel):
    """Lightweight schema validation for a Pebble HTTP check."""

    url: pydantic.AnyHttpUrl
    headers: Optional[Dict[str, str]]

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        extra = "forbid"


class TcpCheck(pydantic.BaseModel):
    """Lightweight schema validation for a Pebble TCP check."""

    port: int
    host: Optional[str]

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        extra = "forbid"


class ExecCheck(pydantic.BaseModel):
    """Lightweight schema validation for a Pebble exec check."""

    command: str
    service_context: Optional[str]
    environment: Optional[Dict[str, str]]
    user: Optional[str]
    user_id: Optional[int]
    group: Optional[str]
    group_id: Optional[int]
    working_dir: Optional[str]

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        alias_generator = lambda s: s.replace("_", "-")  # noqa: E731
        extra = "forbid"


class Check(pydantic.BaseModel):
    """Lightweight schema validation for a Pebble checks.

    Based on
    https://github.com/canonical/pebble#layer-specification
    """

    override: Literal["merge", "replace"]
    level: Optional[Literal["alive", "ready"]]
    period: Optional[str]
    timeout: Optional[str]
    threshold: Optional[int]
    http: Optional[HttpCheck]
    tcp: Optional[TcpCheck]
    exec: Optional[ExecCheck]

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

        raise ProjectValidationError(err)

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        alias_generator = lambda s: s.replace("_", "-")  # noqa: E731
        extra = "forbid"


class Service(pydantic.BaseModel):
    """Lightweight schema validation for a Pebble service.

    Based on
    https://github.com/canonical/pebble#layer-specification
    """

    override: Literal["merge", "replace"]
    command: str
    summary: Optional[str]
    description: Optional[str]
    startup: Optional[Literal["enabled", "disabled"]]
    after: Optional[List[str]]
    before: Optional[List[str]]
    requires: Optional[List[str]]
    environment: Optional[Dict[str, str]]
    user: Optional[str]
    user_id: Optional[int]
    group: Optional[str]
    group_id: Optional[int]
    working_dir: Optional[str]
    on_success: Optional[Literal["restart", "shutdown", "ignore"]]
    on_failure: Optional[Literal["restart", "shutdown", "ignore"]]
    on_check_failure: Optional[Dict[str, Literal["restart", "shutdown", "ignore"]]]
    backoff_delay: Optional[str]
    backoff_factor: Optional[float]
    backoff_limit: Optional[str]
    kill_delay: Optional[str]

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        alias_generator = lambda s: s.replace("_", "-")  # noqa: E731
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
        layer_content: Dict[str, Any],
        rock_name: str,
    ) -> None:
        """Infers and defines a new Pebble layer file.

        Infers the Pebble layer filename based on the existing contents of
        ref_fs and writes the layer content into target_dir.

        :param target_dir: Path where to write the new Pebble layer file
        :param ref_fs: filesystem to use as a reference when inferring the layer name
        :param layer_content: the actual Pebble layer, in JSON
        :param rock_name: name of the ROCK where the layer will end up
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
