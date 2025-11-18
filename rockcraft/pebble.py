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

import enum
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, Any, Literal

import annotated_types
import pydantic
import yaml
from craft_application.errors import CraftValidationError
from craft_application.models import CraftBaseModel
from craft_cli import emit


class SuccessExitState(enum.Enum):
    """What to do on exit success."""

    RESTART = "restart"
    """Restart the service after the backoff delay."""
    SHUTDOWN = "shutdown"
    """Shut down the pebble daemon (with exit code 0)"""
    FAILURE_SHUTDOWN = "failure-shutdown"
    """Shut down the pebble daemon (with exit code 10)"""
    IGNORE = "ignore"
    """Do nothing further."""


class FailureExitState(enum.Enum):
    """What to do on a failure exit."""

    RESTART = "restart"
    """Restart the service after the backoff delay."""
    SHUTDOWN = "shutdown"
    """Shut down the pebble daemon (with exit code 10)"""
    SUCCESS_SHUTDOWN = "success-shutdown"
    """Shut down the pebble daemon (with exit code 0)"""
    IGNORE = "ignore"
    """Do nothing further."""


class HttpCheckOptions(CraftBaseModel):
    """Lightweight schema validation for a Pebble HTTP check."""

    url: pydantic.AnyHttpUrl = pydantic.Field(
        description="The URL to fetch",
        examples=["https://example.com/foo", "http://localhost/health-check"],
    )
    headers: dict[str, str] | None = pydantic.Field(
        default=None,
        description="Headers to send with the HTTP request.",
        examples=[{"X-Health-Check": "true"}],
    )


class TcpCheckOptions(CraftBaseModel):
    """Lightweight schema validation for a Pebble TCP check."""

    port: int = pydantic.Field(
        description="The TCP port to check is open.",
        ge=1,
        le=65535,
    )
    host: str | None = pydantic.Field(
        default=None,
        description="The hostname or IP address to check. Defaults to 'localhost'.",
        examples=["localhost", "::1", "127.0.0.1"],
    )


class ExecCheckOptions(CraftBaseModel):
    """Lightweight schema validation for a Pebble exec check."""

    command: str = pydantic.Field(
        description="The command to execute for this health check.",
        examples=["/usr/bin/health-check"],
    )
    service_context: str | None = pydantic.Field(
        default=None,
        description=(
            "Run the check as the given service's user and group, with that service's "
            "working directory and environment variables set."
        ),
    )
    """Run the check in the context of the given service.

    Inherits the service's environment variables, user, group and working directory.

    Any values specified on the check directly will override that service context.
    """
    environment: dict[str, str] | None = pydantic.Field(
        default=None,
        description="A mapping of environment variables with which to run the check.",
    )
    user: str | None = pydantic.Field(
        default=None, description="The user that will run the check."
    )
    user_id: Annotated[int, annotated_types.Ge(0)] | None = pydantic.Field(
        default=None,
        description="The UID of the user that will run the check.",
    )
    group: str | None = pydantic.Field(
        default=None, description="The group name for the check process to run as."
    )
    group_id: Annotated[int, annotated_types.Ge(0)] | None = pydantic.Field(
        default=None,
        description="The GID of the group that will run the check.",
    )
    working_dir: str | None = pydantic.Field(
        default=None, description="The working directory in which the command will run."
    )


class _BaseCheck(CraftBaseModel):
    """Lightweight schema validation for a Pebble checks.

    Based on
    https://canonical-pebble.readthedocs-hosted.com/en/latest/reference/layer-specification/
    """

    override: Literal["merge", "replace"] = pydantic.Field(
        description="How this check is combined with another same-named check.",
    )
    """How this check is combined with another same-named check.

    The value 'merge' will ensure that values in this layer specification are
    merged over existing definitions, whereas 'replace' will entirely override
    the existing check spec in the plan with the same name."""
    level: Literal["alive", "ready"] | None = pydantic.Field(
        default=None,
        description="Check level, used for filtering checks when calling the health endpoint.",
    )
    """Check level, used for filtering checks when calling the health endpoint.

    ``ready`` implies ``alive``, and not ``alive`` implies not ``ready``,
    but not the other way around.
    More information is available in the pebble documentation:
    :external+pebble:doc:`reference/health-checks`
    """
    period: str | None = pydantic.Field(
        default=None,
        description="How frequently to run this check.",
        examples=["10s", "30m"],
    )
    timeout: str | None = pydantic.Field(
        default=None,
        description="The time before the check fails if not completed. Must be less than ``period``.",
        examples=["5s", "2m"],
    )
    threshold: Annotated[int, annotated_types.Ge(1)] | None = pydantic.Field(
        default=None,
        description="Number of consecutive errors before the check is considered failed.",
    )


class HttpCheck(_BaseCheck):
    """Model for a check that uses HTTP."""

    http: HttpCheckOptions


class TcpCheck(_BaseCheck):
    """Model for a check that uses TCP."""

    tcp: TcpCheckOptions


class ExecCheck(_BaseCheck):
    """Model for a check that executes a command."""

    exec: ExecCheckOptions


def _get_check_tag(check: Mapping[str, Any]) -> str:
    tags = ("http", "tcp", "exec")
    check_types = check.keys() & tags
    match len(check_types):
        case 0:
            raise CraftValidationError(
                f"Must specify exactly one of {', '.join(tags)} for each check."
            )
        case 1:
            return check_types.pop()
        case _:
            raise CraftValidationError(
                f"Multiple check types specified ({', '.join(sorted(check_types))}). "
                "Each check must have exactly one type."
            )


Check = Annotated[
    Annotated[HttpCheck, pydantic.Tag("http")]
    | Annotated[TcpCheck, pydantic.Tag("tcp")]
    | Annotated[ExecCheck, pydantic.Tag("exec")],
    pydantic.Discriminator(_get_check_tag),
]
"""Union model allowing the selection of exactly one check type."""


class Service(CraftBaseModel):
    """Lightweight schema validation for a Pebble service.

    Based on
    https://canonical-pebble.readthedocs-hosted.com/en/latest/reference/layer-specification/
    """

    override: Literal["merge", "replace"] = pydantic.Field(
        description="Whether to replace pre-existing service definitions or merge them.",
    )
    """How this service definition is combined with another same-named service.

    The value ``merge`` will ensure that values in this layer specification are merged
    over existing definitions, whereas ``replace`` will entirely override an existing
    service spec in the plan with the same name.
    """
    command: str = pydantic.Field(
        description="The command used to run the service.",
        examples=["/usr/bin/ls", "/usr/bin/somedaemon --db=/db/path [ --port 8080 ]"],
    )
    """The command to run the service.

    This command is executed directly, not interpreted by a shell. May be optionally
    suffixed by default arguments within square brackets, which may be overridden via
    pebble's ``--args`` parameter.
    """
    summary: str | None = pydantic.Field(
        default=None,
        description="A short summary of the service.",
    )
    description: str | None = pydantic.Field(
        default=None,
        description="A detailed, potentially multi-line, description of the service.",
    )
    startup: Literal["enabled", "disabled"] | None = pydantic.Field(
        default=None,
        description="Whether the service is enabled automatically when the rock starts.",
    )
    """Whether the service is enabled automatically when the rock starts.

    If not provided, defaults to ``disabled``."""
    after: list[str] | None = pydantic.Field(
        default=None,
        description="The names of other services that this service should start after.",
    )
    before: list[str] | None = pydantic.Field(
        default=None,
        description="The names of other services that this service should start before.",
    )
    requires: list[str] | None = pydantic.Field(
        default=None,
        description="The names of other services that this service requires in order to start.",
    )
    environment: dict[str, str] | None = pydantic.Field(
        default=None,
        description="Environment variables to set for this process.",
    )
    user: str | None = pydantic.Field(
        default=None,
        description="Run the service as this user.",
    )
    """Run the service as the given user.

    The user must exist in the rock or this will cause a runtime failure.
    """
    user_id: int | None = pydantic.Field(
        default=None, description="Run the service with this user ID."
    )
    """Run the service with this user ID.

    If both ``user-id`` and ``user`` are provided, they must refer to the same user.
    The user ID must exist in the rock or this will cause a runtime failure.
    """
    group: str | None = pydantic.Field(
        default=None,
        description="Run the service as this group.",
    )
    """Run the service with the group ID of the given group.

    The group must exist in the rock or this will cause a runtime failure.
    """
    group_id: int | None = pydantic.Field(
        default=None, description="Run the service with this group ID."
    )
    """Run the service with this group ID.

    If both ``group-id`` and ``group`` are provided, they must refer to the same group.
    The group ID must exist in the rock or this will cause a runtime failure.
    """
    working_dir: str | None = pydantic.Field(
        default=None,
        description="Working directory for the service command.",
    )
    on_success: SuccessExitState | None = pydantic.Field(
        default=None,
        description="What to do when the service exits with success.",
    )
    on_failure: FailureExitState | None = pydantic.Field(
        default=None,
        description="What to do when the service exits with an error.",
    )
    on_check_failure: dict[str, FailureExitState] | None = pydantic.Field(
        default=None,
        description="What to do when a health check fails.",
    )
    backoff_delay: str | None = pydantic.Field(
        default=None,
        description="Initial backoff delay for the 'restart' exit action.",
        examples=["500ms", "10s"],
    )
    backoff_factor: Annotated[float, annotated_types.Ge(1.0)] | None = pydantic.Field(
        default=None,
        description="Multiplication factor for backoff delay.",
        examples=["2.0", "1.000001"],
    )
    """Multiplication factor for backoff delay.

    After each backoff, the current delay is multiplied by this factor to get the next
    backoff delay. Must be greater than or equal to 1.
    """
    backoff_limit: str | None = pydantic.Field(
        default=None,
        description="Maximum backoff delay.",
        examples=["30s", "1m"],
    )
    """Maximum backoff delay.

    When multiplying by ``backoff-factor`` to get the next ``backoff-delay``, if the
    result is greater than this value, it is capped to this value.

    For example, a service with ``backoff-delay`` of 2s, ``backoff-factor`` of 2 and
    ``backoff-limit`` of 5s will delay for 2 seconds, then 4 seconds, then 5 seconds.
    """
    kill_delay: str | None = pydantic.Field(
        default=None,
        description="How long to wait after a SIGTERM and exit pebble uses SIGKILL.",
        examples=["10s", "1m"],
    )


class Pebble:
    """Handles the Pebble metadata information and setup operations."""

    PEBBLE_PATH = "var/lib/pebble/default"
    PEBBLE_LAYERS_PATH = f"{PEBBLE_PATH}/layers"
    PEBBLE_BINARY_DIR = "usr/bin"
    PEBBLE_BINARY_PATH = f"{PEBBLE_BINARY_DIR}/pebble"
    PEBBLE_BINARY_PATH_PREVIOUS = "bin/pebble"
    _BASE_PART_SPEC = {
        "plugin": "nil",
        "stage-snaps": ["pebble/latest/stable"],
        # We need this because "services" is Optional, but the directory must exist
        "override-prime": str(
            f"craftctl default\n/usr/bin/mkdir -p {PEBBLE_LAYERS_PATH}\n/usr/bin/chmod 777 {PEBBLE_PATH}"
        ),
    }
    # The part spec for 25.10 and newer; pebble is in "usr/bin/pebble" because of the
    # usrmerged install dir.
    PEBBLE_PART_SPEC = {
        **_BASE_PART_SPEC,
        "stage": [PEBBLE_BINARY_PATH],
        # need the build-attribute at the moment because the usrmerged install is not
        # created for parts with the 'nil' plugin.
        "build-attributes": ["enable-usrmerge"],
    }
    # The part spec used for 24.04, where we organize "bin/pebble" to "usr/bin/pebble"
    PEBBLE_PART_SPEC_2404 = {
        **_BASE_PART_SPEC,
        "organize": {"bin": PEBBLE_BINARY_DIR},
        "stage": [PEBBLE_BINARY_PATH],
    }
    # The part spec for 22.04 and 20.04, where pebble is "bin/pebble"
    PEBBLE_PART_SPEC_2204_2004 = {
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
        pebble_layers_path_in_base = ref_fs / self.PEBBLE_LAYERS_PATH

        existing_pebble_layers: list[Path] = [
            *pebble_layers_path_in_base.glob("[0-9][0-9][0-9]-???*.yaml"),
            *pebble_layers_path_in_base.glob("[0-9][0-9][0-9]-???*.yml"),
        ]

        prefixes = [Path(layer).name[:3] for layer in existing_pebble_layers]
        prefixes.sort()
        emit.progress(
            f"Found {len(existing_pebble_layers)} Pebble layers in the base's root filesystem"
        )

        new_layer_prefix = f"{(int(prefixes[-1]) + 1):03}" if prefixes else "001"
        new_layer_name = f"{new_layer_prefix}-rockcraft-{rock_name}.yaml"

        emit.progress(f"Preparing new Pebble layer file {new_layer_name}")

        tmp_pebble_layers_path = target_dir / self.PEBBLE_LAYERS_PATH
        tmp_pebble_layers_path.mkdir(parents=True)
        (target_dir / self.PEBBLE_PATH).chmod(0o777)

        tmp_new_layer = tmp_pebble_layers_path / new_layer_name
        with tmp_new_layer.open("w", encoding="utf-8") as layer_fd:
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

        if Pebble._is_noble(build_base):
            part_spec = Pebble.PEBBLE_PART_SPEC_2404
        elif Pebble._is_focal_or_jammy(build_base):
            part_spec = Pebble.PEBBLE_PART_SPEC_2204_2004

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

    @staticmethod
    def _is_noble(build_base: str) -> bool:
        return build_base == "ubuntu@24.04"


def add_pebble_part(project: dict[str, Any]) -> None:
    """Add pebble-specific contents to YAML-loaded data.

    This function adds a special "pebble" part to a project's specification, to be
    (eventually) used as the image's entrypoint.

    :param project: The project spec loaded from "rockcraft.yaml" by the project
      service.
    :raises CraftValidationError: If `project` already contains a "pebble" part,
      and said part's contents are different from the contents of the part we add.
    """
    # at least base should be required, but YAML has not been validated yet
    build_base = project.get("build-base") or project.get("base")
    if build_base is None:
        # don't try to add the relevant pebble part if base is missing
        # (friendly error message will be presented later from pydantic)
        return
    pebble_part = Pebble.get_part_spec(build_base)

    parts = project["parts"]
    if "pebble" in parts:
        if parts["pebble"] == pebble_part:
            # Project already has the correct pebble part.
            return
        # Project already has a pebble part, and it's different from ours;
        # this is currently not supported.
        raise CraftValidationError('Cannot change the default "pebble" part')

    parts["pebble"] = pebble_part
