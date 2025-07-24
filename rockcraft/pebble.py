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
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import pydantic
import yaml
from craft_application.errors import CraftValidationError
from craft_application.models import CraftBaseModel
from craft_cli import emit


class HttpCheck(CraftBaseModel):
    """Lightweight schema validation for a Pebble HTTP check."""

    url: pydantic.AnyHttpUrl
    headers: dict[str, str] | None = None


class TcpCheck(CraftBaseModel):
    """Lightweight schema validation for a Pebble TCP check."""

    port: int
    host: str | None = None


class ExecCheck(CraftBaseModel):
    """Lightweight schema validation for a Pebble exec check."""

    command: str
    service_context: str | None = None
    environment: dict[str, str] | None = None
    user: str | None = None
    user_id: int | None = None
    group: str | None = None
    group_id: int | None = None
    working_dir: str | None = None


class Check(CraftBaseModel):
    """Lightweight schema validation for a Pebble checks.

    Based on
    https://canonical-pebble.readthedocs-hosted.com/en/latest/reference/layer-specification/
    """

    override: Literal["merge", "replace"]
    level: Literal["alive", "ready"] | None = None
    period: str | None = None
    timeout: str | None = None
    threshold: int | None = None
    http: HttpCheck | None = None
    tcp: TcpCheck | None = None
    exec: ExecCheck | None = None

    @pydantic.model_validator(mode="before")
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


class Service(CraftBaseModel):
    """Lightweight schema validation for a Pebble service.

    Based on
    https://canonical-pebble.readthedocs-hosted.com/en/latest/reference/layer-specification/
    """

    override: Literal["merge", "replace"]
    command: str
    summary: str | None = None
    description: str | None = None
    startup: Literal["enabled", "disabled"] | None = None
    after: list[str] | None = None
    before: list[str] | None = None
    requires: list[str] | None = None
    environment: dict[str, str] | None = None
    user: str | None = None
    user_id: int | None = None
    group: str | None = None
    group_id: int | None = None
    working_dir: str | None = None
    on_success: Literal["restart", "shutdown", "ignore"] | None = None
    on_failure: Literal["restart", "shutdown", "ignore"] | None = None
    on_check_failure: dict[str, Literal["restart", "shutdown", "ignore"]] | None = None
    backoff_delay: str | None = None
    backoff_factor: float | None = None
    backoff_limit: str | None = None
    kill_delay: str | None = None


class Pebble:
    """Handles the Pebble metadata information and setup operations."""

    PEBBLE_PATH = "var/lib/pebble/default"
    PEBBLE_LAYERS_PATH = f"{PEBBLE_PATH}/layers"
    PEBBLE_BINARY_DIR = "usr/bin"
    PEBBLE_BINARY_PATH = f"{PEBBLE_BINARY_DIR}/pebble"
    PEBBLE_BINARY_PATH_PREVIOUS = "bin/pebble"
    _BASE_PART_SPEC = {
        "plugin": "go",
        "source": "https://github.com/canonical/pebble.git",
        "source-type": "git",
        "source-tag": "v1.18.0",
        "build-snaps": ["go/1.23-fips/stable"],
        # We need this because "services" is Optional, but the directory must exist
        "override-prime": str(
            f"craftctl default\nmkdir -p {PEBBLE_LAYERS_PATH}\nchmod 777 {PEBBLE_PATH}"
        ),
    }
    PEBBLE_PART_SPEC = {
        **_BASE_PART_SPEC,
        "organize": {"bin": PEBBLE_BINARY_DIR},
        "stage": [PEBBLE_BINARY_PATH],
    }
    PEBBLE_PART_SPEC_PREVIOUS = {
        **_BASE_PART_SPEC,
        "stage": [PEBBLE_BINARY_PATH_PREVIOUS],
    }
    # This is the value that Pebble sets to the PATH env var if it's empty.
    # (https://github.com/canonical/pebble/blob/master/internals/overlord/cmdstate/request.go#L91)
    DEFAULT_ENV_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

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

        prefixes = [Path(layer).name[:3] for layer in existing_pebble_layers]
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

    @staticmethod
    def get_part_spec(build_base: str) -> dict[str, Any]:
        """Get the part providing the pebble binary for a given build base."""
        part_spec: dict[str, Any] = Pebble.PEBBLE_PART_SPEC

        if Pebble._is_focal_or_jammy(build_base):
            part_spec = Pebble.PEBBLE_PART_SPEC_PREVIOUS

        return part_spec

    @staticmethod
    def get_entrypoint(build_base: str) -> list[str]:
        """Get the rock's entry point for a given build base."""
        is_legacy = Pebble._is_focal_or_jammy(build_base)

        pebble_path = Pebble.PEBBLE_BINARY_PATH
        if is_legacy:
            # Previously pebble existed in /bin/pebble
            pebble_path = Pebble.PEBBLE_BINARY_PATH_PREVIOUS

        return [f"/{pebble_path}", "enter"]

    @staticmethod
    def _is_focal_or_jammy(build_base: str) -> bool:
        return build_base in ("ubuntu@20.04", "ubuntu@22.04")
