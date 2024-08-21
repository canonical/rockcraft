# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021,2024 Canonical Ltd.
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

"""Project definition and helpers."""
import copy
import re
import shlex
import typing
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import craft_cli
import pydantic
import spdx_lookup  # type: ignore
import yaml
from craft_application.errors import CraftValidationError
from craft_application.models import (
    BuildPlanner as BaseBuildPlanner,
    get_validator_by_regex,
)
from craft_application.models import Platform
from craft_application.models import Project as BaseProject
from craft_application.models.base import alias_generator
from craft_providers import bases
from craft_providers.errors import BaseConfigurationError
from typing_extensions import Annotated, override

from rockcraft.architectures import SUPPORTED_ARCHS
from rockcraft.errors import ProjectLoadError
from rockcraft.extensions import apply_extensions
from rockcraft.parts import part_has_overlay
from rockcraft.pebble import Check, Pebble, Service
from rockcraft.usernames import SUPPORTED_GLOBAL_USERNAMES

# pyright workaround
if TYPE_CHECKING:
    _RunUser = str | None
else:
    _RunUser = Literal[tuple(SUPPORTED_GLOBAL_USERNAMES)] | None


PROJECT_NAME_REGEX = r"^([a-z](?:-?[a-z0-9]){2,})$"
_PROJECT_NAME_DESCRIPTION = """\
Valid names for rocks. It matches the accepted values for pebble layer files:

- must start with a lowercase letter [a-z]
- must contain only lowercase letters [a-z], numbers [0-9] or hyphens
- must not end with a hyphen, and must not contain two or more consecutive hyphens
"""
_PROJECT_NAME_COMPILED_REGEX = re.compile(PROJECT_NAME_REGEX)

MESSAGE_INVALID_NAME = (
    "invalid name for rock: Names can only use ASCII lowercase letters, numbers, and hyphens. "
    "They must start with a lowercase letter, may not end with a hyphen, "
    "and may not have two hyphens in a row."
)

DEPRECATED_COLON_BASES = ["ubuntu:20.04", "ubuntu:22.04"]


ProjectName = Annotated[
    str,
    pydantic.BeforeValidator(
        get_validator_by_regex(_PROJECT_NAME_COMPILED_REGEX, MESSAGE_INVALID_NAME)
    ),
    pydantic.Field(
        min_length=1,
        strict=True,
        pattern=PROJECT_NAME_REGEX,
        description=_PROJECT_NAME_DESCRIPTION,
        title="Project Name",
    ),
]

BaseT = Literal["bare", "ubuntu@20.04", "ubuntu@22.04", "ubuntu@24.04"]
BuildBaseT = typing.Annotated[
    Literal["ubuntu@20.04", "ubuntu@22.04", "ubuntu@24.04", "devel"] | None,
    pydantic.Field(validate_default=True),
]


class BuildPlanner(BaseBuildPlanner):
    """BuildPlanner for Rockcraft projects."""

    platforms: dict[str, Platform]  # type: ignore[assignment]
    base: BaseT  # type: ignore[reportIncompatibleVariableOverride]
    build_base: BuildBaseT = None  # type: ignore[reportIncompatibleVariableOverride]

    @pydantic.field_validator("build_base")
    @classmethod
    def _validate_build_base(
        cls, value: str | None, info: pydantic.ValidationInfo
    ) -> str | None:
        """Build-base defaults to the base value if not specified.

        :raises CraftValidationError: If base validation fails.
        """
        if not value:
            base_value = info.data.get("base")
            if base_value == "bare":
                raise ValueError('When "base" is bare, a build-base must be specified.')
            return base_value
        return value

    @pydantic.field_validator("base", mode="before")
    @classmethod
    def _validate_deprecated_base(cls, base_value: str | None) -> str | None:
        return cls._check_deprecated_base(base_value, "base")

    @pydantic.field_validator("build_base", mode="before")
    @classmethod
    def _validate_deprecated_build_base(cls, base_value: str | None) -> str | None:
        return cls._check_deprecated_base(base_value, "build-base")

    @staticmethod
    def _check_deprecated_base(base_value: str | None, field_name: str) -> str | None:
        if base_value in DEPRECATED_COLON_BASES:
            at_value = base_value.replace(":", "@")
            message = (
                f'Warning: use of ":" in field "{field_name}" is deprecated. '
                f'Prefer "{at_value}" instead.'
            )
            craft_cli.emit.message(message)
            return at_value

        return base_value

    @pydantic.field_validator("platforms", mode="before")
    @classmethod
    def _vectorise_build_for(cls, platforms: dict[str, Any]) -> dict[str, Any]:
        """Vectorise target architecture if needed."""
        for platform in platforms.values():
            if not platform:
                continue
            if isinstance(platform.get("build-for"), str):
                platform["build-for"] = [platform["build-for"]]
        return platforms

    @pydantic.field_validator("platforms")
    @classmethod
    def _validate_all_platforms(
        cls, platforms: dict[str, Platform]
    ) -> dict[str, Platform]:
        """Make sure all provided platforms are tangible and sane."""
        for platform_label, platform in platforms.items():
            error_prefix = f"Error for platform entry '{platform_label}'"

            # build_on and build_for are validated
            # let's also validate the platform label
            build_on_one_of = platform.build_on or [platform_label]

            # If the label maps to a valid architecture and
            # `build-for` is present, then both need to have the same value,
            # otherwise the project is invalid.
            if platform.build_for:
                build_target = platform.build_for[0]
                if platform_label in SUPPORTED_ARCHS and platform_label != build_target:
                    raise ValueError(
                        str(
                            f"{error_prefix}: if 'build-for' is provided and the "
                            "platform entry label corresponds to a valid architecture, then "
                            f"both values must match. {platform_label} != {build_target}"
                        )
                    )
            else:
                build_target = platform_label

            # Both build and target architectures must be supported
            if not any(b_o in SUPPORTED_ARCHS for b_o in build_on_one_of):
                raise ValueError(
                    str(
                        f"{error_prefix}: trying to build rock in one of "
                        f"{build_on_one_of}, but none of these build architectures is supported. "
                        f"Supported architectures: {list(SUPPORTED_ARCHS.keys())}"
                    )
                )

            if build_target not in SUPPORTED_ARCHS:
                raise ValueError(
                    str(
                        f"{error_prefix}: trying to build rock for target "
                        f"architecture {build_target}, which is not supported. "
                        f"Supported architectures: {list(SUPPORTED_ARCHS.keys())}"
                    )
                )

        return platforms

    @property
    def effective_base(self) -> bases.BaseName:
        """Get the Base name for craft-providers."""
        base = self.build_base if self.build_base else self.base

        if base == "devel":
            name, channel = "ubuntu", "devel"
        else:
            name, channel = base.split("@")

        return bases.BaseName(name, channel)

    @override
    @classmethod
    def model_reference_slug(cls) -> str | None:
        return "/reference/rockcraft.yaml"


class Project(BuildPlanner, BaseProject):  # type: ignore[misc]
    """Rockcraft project definition."""

    name: ProjectName  # type: ignore
    # summary is Optional[str] in BaseProject
    summary: str  # type: ignore
    description: str  # type: ignore[reportIncompatibleVariableOverride]
    # license is Optional[str] in BaseProject
    environment: dict[str, str] | None = None
    run_user: _RunUser = None
    services: dict[str, Service] | None = None
    checks: dict[str, Check] | None = None
    entrypoint_service: str | None = None
    platforms: dict[str, Platform | None]  # type: ignore[assignment]

    model_config = pydantic.ConfigDict(
        validate_assignment=True,
        extra="forbid",
        populate_by_name=True,
        alias_generator=alias_generator,
        frozen=True,
    )

    @override
    @classmethod
    def _providers_base(cls, base: str) -> bases.BaseAlias | None:
        """Get a BaseAlias from rockcraft's base.

        :param base: The base name.

        :returns: The BaseAlias for the base or None for bare bases.
        :raises ValueError: If the project's base cannot be determined.
        """
        if base == "bare":
            return None

        if base == "devel":
            return bases.get_base_alias(("ubuntu", "devel"))

        try:
            name, channel = base.split("@")
            return bases.get_base_alias(bases.BaseName(name, channel))
        except (ValueError, BaseConfigurationError) as err:
            raise ValueError(f"Unknown base {base!r}") from err

    @pydantic.model_validator(mode="before")
    @classmethod
    def _check_unsupported_options(cls, values: Mapping[str, Any]) -> Mapping[str, Any]:
        """Before validation, check if unsupported fields exist. Exit if so."""
        # pylint: disable=unused-argument
        unsupported_msg = str(
            "The fields 'entrypoint', 'cmd' and 'env' are not supported in "
            "Rockcraft. All rocks have Pebble as their entrypoint, so you must "
            "use 'services' to define your container application and "
            "respective environment."
        )
        unsupported_fields = ["cmd", "entrypoint", "env"]
        if any(field in values for field in unsupported_fields):
            raise ValueError(unsupported_msg)

        return values

    @pydantic.field_validator("license")
    @classmethod
    def _validate_license(
        cls, license: str | None  # pylint: disable=redefined-builtin
    ) -> str | None:
        """Make sure the provided license is valid and in SPDX format."""
        if not license:
            return None

        if license == "proprietary":
            # This is the license name we use on our stores.
            return license

        lic: spdx_lookup.License | None = spdx_lookup.by_id(license)  # type: ignore[reportUnknownMemberType]
        if lic is None:
            raise ValueError(
                f"License {license} not valid. It must be either 'proprietary' or in SPDX format.",
            )
        return str(lic.id)  # type: ignore[reportUnknownMemberType]

    @pydantic.model_validator(mode="before")
    @classmethod
    def _validate_title(cls, values: dict[str, Any]) -> dict[str, Any]:
        """If title is not provided, it defaults to the provided rock name."""
        if not values.get("title"):
            values["title"] = values.get("name")
        return values

    @pydantic.field_validator("parts")
    @classmethod
    def _validate_base_and_overlay(
        cls, parts: dict[str, Any], info: pydantic.ValidationInfo
    ) -> dict[str, Any]:
        """Projects with "bare" bases cannot use overlays."""
        if info.data.get("base") != "bare":
            return parts

        for part_name, part in parts.items():
            if part_has_overlay(part):
                raise ValueError(
                    f"Part '{part_name}' cannot use overlays with a 'bare' base"
                    " (there is no system to overlay)."
                )
        return parts

    @pydantic.field_validator("entrypoint_service")
    @classmethod
    def _validate_entrypoint_service(
        cls, entrypoint_service: str | None, info: pydantic.ValidationInfo
    ) -> str | None:
        """Verify that the entrypoint_service exists in the services dict."""
        craft_cli.emit.message(
            "Warning: defining an entrypoint-service will result in a rock with "
            + "an atypical OCI Entrypoint. While that might be acceptable for "
            + "testing and personal use, it shall require prior approval before "
            + "submitting to a Canonical registry namespace."
        )

        if entrypoint_service not in info.data.get("services", {}):
            raise ValueError(
                f"The provided entrypoint-service '{entrypoint_service}' is not "
                + "a valid Pebble service."
            )

        command = info.data["services"][entrypoint_service].command
        command_sh_args = shlex.split(command)
        # optional arg is surrounded by brackets, so check that they exist in the
        # right order
        try:
            if command_sh_args.index("[") >= command_sh_args.index("]"):
                raise IndexError(
                    "Bad syntax for the entrypoint-service command's"
                    + " additional args."
                )
        except ValueError as ex:
            raise ValueError(
                f"The Pebble service '{entrypoint_service}' has a command "
                + f"{command} without default arguments and thus cannot be used "
                + "as the entrypoint-service."
            ) from ex

        return entrypoint_service

    @pydantic.field_validator("environment")
    @classmethod
    def _forbid_env_var_bash_interpolation(
        cls, environment: dict[str, str] | None
    ) -> dict[str, str]:
        """Variable interpolation isn't yet supported, so forbid attempts to do it."""
        if not environment:
            return {}

        values_with_dollar_signs = list(
            filter(lambda v: "$" in str(v[:-1]), environment.values())
        )
        if values_with_dollar_signs:
            raise ValueError(
                str(
                    "String interpolation not allowed for: "
                    f"{' ; '.join(values_with_dollar_signs)}"
                )
            )

        return environment

    def generate_metadata(
        self, generation_time: str, base_digest: bytes
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Generate the rock's metadata (both the OCI annotation and internal metadata.

        :param generation_time: the UTC time at the time of calling this method
        :param base_digest: digest of the base image

        :return: both the OCI annotation and internal metadata, as a tuple
        """
        metadata = {
            "name": self.name,
            "summary": self.summary,
            "title": self.title,
            "version": self.version,
            "created": generation_time,
            "base": self.base,
            "base-digest": base_digest.hex(),
        }

        if self.build_base == "devel":
            # Annotate that this project was built with a development base.
            metadata["grade"] = "devel"

        annotations = {
            "org.opencontainers.image.version": self.version,
            "org.opencontainers.image.title": self.title,
            "org.opencontainers.image.ref.name": self.name,
            "org.opencontainers.image.created": generation_time,
            "org.opencontainers.image.base.digest": base_digest.hex(),
        }
        if self.license:
            annotations["org.opencontainers.image.licenses"] = self.license

        return (annotations, metadata)

    @override
    @classmethod
    def transform_pydantic_error(cls, error: pydantic.ValidationError) -> None:
        BaseProject.transform_pydantic_error(error)

        for error_dict in error.errors():
            loc = str(error_dict["loc"][0]) if error_dict["loc"] else ""
            loc_and_type = (loc, error_dict["type"])
            if loc_and_type == ("name", "value_error.str.regex"):
                # Note: The base Project class already changes the error message
                # for the "name" regex, but we re-change it here because
                # Rockcraft's name regex is slightly stricter.
                error_dict["msg"] = MESSAGE_INVALID_NAME

    @override
    @classmethod
    def model_reference_slug(cls) -> str | None:
        return "/reference/rockcraft.yaml"


def load_project(filename: Path) -> dict[str, Any]:
    """Load and unmarshal the project YAML file.

    :param filename: The YAML file to load.

    :returns: The populated project data.

    :raises ProjectLoadError: If loading fails.
    :raises CraftValidationError: If data validation fails.
    """
    try:
        with open(filename, encoding="utf-8") as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
    except OSError as err:
        msg = err.strerror
        if err.filename:
            msg = f"{msg}: {err.filename!r}."
        raise ProjectLoadError(msg) from err

    yaml_data = transform_yaml(filename.parent, yaml_data)

    return yaml_data


def transform_yaml(project_root: Path, yaml_data: dict[str, Any]) -> dict[str, Any]:
    """Do Rockcraft-specific transformations on a project yaml.

    :param project_root: The path that contains the "rockcraft.yaml" file.
    :param yaml_data: The data dict loaded from the yaml file.
    """
    yaml_data = apply_extensions(project_root, yaml_data)

    _add_pebble_data(yaml_data)

    return yaml_data


def _add_pebble_data(yaml_data: dict[str, Any]) -> None:
    """Add pebble-specific contents to YAML-loaded data.

    This function adds a special "pebble" part to a project's specification, to be
    (eventually) used as the image's entrypoint.

    :param yaml_data: The project spec loaded from "rockcraft.yaml".
    :raises CraftValidationError: If `yaml_data` already contains a "pebble" part.
    """
    if "parts" not in yaml_data:
        # Invalid project: let it return to fail in the regular validation flow.
        return

    parts = yaml_data["parts"]
    if "pebble" in parts:
        # Project already has a pebble part: this is not supported.
        raise CraftValidationError('Cannot override the default "pebble" part')

    # do not modify the original data with pre-validators
    model = BuildPlanner.unmarshal(copy.deepcopy(yaml_data))
    build_base = model.build_base if model.build_base else model.base

    parts["pebble"] = Pebble.get_part_spec(build_base)
