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

"""Project definition and helpers."""
import re
import shlex
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

import craft_cli
import pydantic
import spdx_lookup  # type: ignore
import yaml
from craft_application.models import BuildInfo
from craft_application.models import Project as BaseProject
from craft_archives import repo
from craft_providers import bases
from pydantic_yaml import YamlModelMixin

from rockcraft.architectures import SUPPORTED_ARCHS
from rockcraft.errors import ProjectLoadError, ProjectValidationError
from rockcraft.extensions import apply_extensions
from rockcraft.parts import part_has_overlay, validate_part
from rockcraft.pebble import Check, Pebble, Service
from rockcraft.usernames import SUPPORTED_GLOBAL_USERNAMES

if TYPE_CHECKING:  # pragma: no cover
    from pydantic.error_wrappers import ErrorDict


class Platform(pydantic.BaseModel):
    """Rockcraft project platform definition."""

    build_on: Optional[  # type: ignore
        pydantic.conlist(str, unique_items=True, min_items=1)  # type: ignore
    ]
    build_for: Optional[  # type: ignore
        pydantic.conlist(str, unique_items=True, min_items=1)  # type: ignore
    ]

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        allow_population_by_field_name = True
        alias_generator = lambda s: s.replace("_", "-")  # noqa: E731

    @pydantic.validator("build_for", pre=True)
    @classmethod
    def _vectorise_build_for(cls, val: Union[str, List[str]]) -> List[str]:
        """Vectorise target architecture if needed."""
        if isinstance(val, str):
            val = [val]
        return val

    @pydantic.root_validator(skip_on_failure=True)
    @classmethod
    def _validate_platform_set(cls, values: Mapping[str, Any]) -> Mapping[str, Any]:
        """Validate the build_on build_for combination."""
        build_for = values["build_for"] if values.get("build_for") else []
        build_on = values["build_on"] if values.get("build_on") else []

        # We can only build for 1 arch at the moment
        if len(build_for) > 1:
            raise ProjectValidationError(
                str(
                    f"Trying to build a ROCK for {build_for} "
                    "but multiple target architectures are not "
                    "currently supported. Please specify only 1 value."
                )
            )

        # If build_for is provided, then build_on must also be
        if not build_on and build_for:
            raise ProjectValidationError(
                "'build_for' expects 'build_on' to also be provided."
            )

        return values


NAME_REGEX = r"^([a-z](?:-?[a-z0-9]){2,})$"
"""
The regex for valid names for ROCKs. It matches the accepted values for pebble
layer files:

- must start with a lowercase letter [a-z]
- must contain only lowercase letters [a-z], numbers [0-9] or hyphens
- must not end with a hyphen, and must not contain two or more consecutive hyphens

(taken from https://github.com/canonical/pebble/blob/dbda12237fef3c4d2739824fce7fa65ba1dad76a/internal/plan/plan.go#L955)
"""

INVALID_NAME_MESSAGE = (
    "Invalid name for ROCK (must contain only lowercase letters, numbers and hyphens)"
)

DEPRECATED_COLON_BASES = ["ubuntu:20.04", "ubuntu:22.04"]


class NameStr(pydantic.ConstrainedStr):
    """Constrained string type only accepting valid ROCK names."""

    regex = re.compile(NAME_REGEX)


class Project(YamlModelMixin, BaseProject):
    """Rockcraft project definition."""

    name: NameStr  # type: ignore
    # summary is Optional[str] in BaseProject
    summary: str  # type: ignore
    description: str
    rock_license: str = pydantic.Field(alias="license")
    platforms: Dict[str, Any]
    base: Literal["bare", "ubuntu@20.04", "ubuntu@22.04"]
    build_base: Optional[Literal["ubuntu@20.04", "ubuntu@22.04"]]
    environment: Optional[Dict[str, str]]
    run_user: Optional[Literal[tuple(SUPPORTED_GLOBAL_USERNAMES)]]  # type: ignore
    services: Optional[Dict[str, Service]]
    checks: Optional[Dict[str, Check]]
    entrypoint_service: Optional[str]

    package_repositories: Optional[List[Dict[str, Any]]]

    parts: Dict[str, Any]

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        validate_assignment = True
        extra = "forbid"
        allow_mutation = False
        allow_population_by_field_name = True
        alias_generator = lambda s: s.replace("_", "-")  # noqa: E731
        error_msg_templates = {
            "value_error.str.regex": INVALID_NAME_MESSAGE,
        }

    @property
    def effective_base(self) -> bases.BaseName:
        """Get the Base name for craft-providers."""
        base = super().effective_base
        name, channel = base.split("@")
        return bases.BaseName(name, channel)

    @pydantic.root_validator(pre=True)
    @classmethod
    def _check_unsupported_options(cls, values: Mapping[str, Any]) -> Mapping[str, Any]:
        """Before validation, check if unsupported fields exist. Exit if so."""
        # pylint: disable=unused-argument
        unsupported_msg = str(
            "The fields 'entrypoint', 'cmd' and 'env' are not supported in "
            "Rockcraft. All ROCKs have Pebble as their entrypoint, so you must "
            "use 'services' to define your container application and "
            "respective environment."
        )
        unsupported_fields = ["cmd", "entrypoint", "env"]
        if any(field in values for field in unsupported_fields):
            raise ProjectValidationError(unsupported_msg)

        return values

    @pydantic.validator("rock_license", always=True)
    @classmethod
    def _validate_license(cls, rock_license: str) -> str:
        """Make sure the provided license is valid and in SPDX format."""
        if rock_license == "proprietary":
            # This is the license name we use on our stores.
            return rock_license

        lic: Optional[spdx_lookup.License] = spdx_lookup.by_id(rock_license)
        if lic is None:
            raise ProjectValidationError(
                f"License {rock_license} not valid. It must be valid and in SPDX format."
            )
        return lic.id

    @pydantic.validator("title", always=True)
    @classmethod
    def _validate_title(cls, title: Optional[str], values: Mapping[str, Any]) -> str:
        """If title is not provided, it defaults to the provided ROCK name."""
        if not title:
            title = values.get("name", "")
        return cast(str, title)

    @pydantic.validator("build_base", always=True)
    @classmethod
    def _validate_build_base(cls, build_base: Optional[str], values: Any) -> str:
        """Build-base defaults to the base value if not specified.

        :raises ProjectValidationError: If base validation fails.
        """
        if not build_base:
            base_value = values.get("base")
            if base_value == "bare":
                raise ProjectValidationError(
                    'When "base" is bare, a build-base must be specified!'
                )
            build_base = values.get("base")
        return cast(str, build_base)

    @pydantic.validator("base", pre=True)
    @classmethod
    def _validate_deprecated_base(cls, base_value: Optional[str]) -> Optional[str]:
        return cls._check_deprecated_base(base_value, "base")

    @pydantic.validator("build_base", pre=True)
    @classmethod
    def _validate_deprecated_build_base(
        cls, base_value: Optional[str]
    ) -> Optional[str]:
        return cls._check_deprecated_base(base_value, "build_base")

    @staticmethod
    def _check_deprecated_base(
        base_value: Optional[str], field_name: str
    ) -> Optional[str]:
        if base_value in DEPRECATED_COLON_BASES:
            at_value = base_value.replace(":", "@")
            message = (
                f'Warning: use of ":" in field "{field_name}" is deprecated. '
                f'Prefer "{at_value}" instead.'
            )
            craft_cli.emit.message(message)
            return at_value

        return base_value

    @pydantic.validator("platforms")
    @classmethod
    def _validate_all_platforms(cls, platforms: Dict[str, Any]) -> Dict[str, Any]:
        """Make sure all provided platforms are tangible and sane."""
        for platform_label in platforms:
            platform = platforms[platform_label] if platforms[platform_label] else {}
            error_prefix = f"Error for platform entry '{platform_label}'"

            # Make sure the provided platform_set is valid
            try:
                platform = Platform(**platform).dict()
            except ProjectValidationError as err:
                # pylint: disable=raise-missing-from
                raise ProjectValidationError(f"{error_prefix}: {str(err)}")

            # build_on and build_for are validated
            # let's also validate the platform label
            build_on_one_of = (
                platform["build_on"] if platform["build_on"] else [platform_label]
            )

            # If the label maps to a valid architecture and
            # `build-for` is present, then both need to have the same value,
            # otherwise the project is invalid.
            if platform["build_for"]:
                build_target = platform["build_for"][0]
                if platform_label in SUPPORTED_ARCHS and platform_label != build_target:
                    raise ProjectValidationError(
                        str(
                            f"{error_prefix}: if 'build_for' is provided and the "
                            "platform entry label corresponds to a valid architecture, then "
                            f"both values must match. {platform_label} != {build_target}"
                        )
                    )
            else:
                build_target = platform_label

            # Both build and target architectures must be supported
            if not any(b_o in SUPPORTED_ARCHS for b_o in build_on_one_of):
                raise ProjectValidationError(
                    str(
                        f"{error_prefix}: trying to build ROCK in one of "
                        f"{build_on_one_of}, but none of these build architectures is supported. "
                        f"Supported architectures: {list(SUPPORTED_ARCHS.keys())}"
                    )
                )

            if build_target not in SUPPORTED_ARCHS:
                raise ProjectValidationError(
                    str(
                        f"{error_prefix}: trying to build ROCK for target "
                        f"architecture {build_target}, which is not supported. "
                        f"Supported architectures: {list(SUPPORTED_ARCHS.keys())}"
                    )
                )

            platforms[platform_label] = platform

        return platforms

    @pydantic.validator("parts", each_item=True)
    @classmethod
    def _validate_parts(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Verify each part (craft-parts will re-validate this)."""
        validate_part(item)
        return item

    @pydantic.validator("parts", each_item=True)
    @classmethod
    def _validate_base_and_overlay(cls, item: Dict[str, Any], values) -> Dict[str, Any]:
        """Projects with "bare" bases cannot use overlays."""
        if values.get("base") == "bare" and part_has_overlay(item):
            raise ProjectValidationError(
                'Overlays cannot be used with "bare" bases (there is no system to overlay).'
            )
        return item

    @pydantic.validator("entrypoint_service")
    @classmethod
    def _validate_entrypoint_service(
        cls, entrypoint_service: Optional[str], values: Any
    ) -> Optional[str]:
        """Verify that the entrypoint_service exists in the services dict."""
        craft_cli.emit.message(
            "Warning: defining an entrypoint-service will result in a rock with "
            + "an atypical OCI Entrypoint. While that might be acceptable for "
            + "testing and personal use, it shall require prior approval before "
            + "submitting to a Canonical registry namespace."
        )

        if entrypoint_service not in values.get("services", {}):
            raise ProjectValidationError(
                f"The provided entrypoint-service '{entrypoint_service}' is not "
                + "a valid Pebble service."
            )

        command = values.get("services")[entrypoint_service].command
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
            raise ProjectValidationError(
                f"The Pebble service '{entrypoint_service}' has a command "
                + f"{command} without default arguments and thus cannot be used "
                + "as the entrypoint-service."
            ) from ex

        return entrypoint_service

    @pydantic.validator("package_repositories")
    @classmethod
    def _validate_package_repositories(
        cls, package_repositories: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        if not package_repositories:
            return []

        errors = []
        for repository in package_repositories:
            try:
                repo.validate_repository(repository)
            except pydantic.ValidationError as exc:
                errors.extend(exc.errors())
        if errors:
            raise ProjectValidationError(
                _format_pydantic_errors(errors, base_location="package-repositories")
            )

        return package_repositories

    @pydantic.validator("environment")
    @classmethod
    def _forbid_env_var_bash_interpolation(
        cls, environment: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """Variable interpolation isn't yet supported, so forbid attempts to do it."""
        if not environment:
            return {}

        values_with_dollar_signs = list(
            filter(lambda v: "$" in str(v[:-1]), environment.values())
        )
        if values_with_dollar_signs:
            raise ProjectValidationError(
                str(
                    "String interpolation not allowed for: "
                    f"{' ; '.join(values_with_dollar_signs)}"
                )
            )

        return environment

    def to_yaml(self) -> str:
        """Dump this project as a YAML string."""

        def _repr_str(dumper, data):
            """Multi-line string representer for the YAML dumper."""
            if "\n" in data:
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        yaml.add_representer(str, _repr_str, Dumper=yaml.SafeDumper)
        return super().yaml(
            by_alias=True,
            exclude_none=True,
            allow_unicode=True,
            sort_keys=False,
            width=1000,
        )

    @classmethod
    def unmarshal(cls, data: Dict[str, Any]) -> "Project":
        """Overridden to raise ProjectValidationError() for Pydantic errors."""
        if not isinstance(data, dict):
            raise TypeError("project data is not a dictionary")

        try:
            project = super().unmarshal(data)
        except pydantic.ValidationError as err:
            raise ProjectValidationError(_format_pydantic_errors(err.errors())) from err

        return project

    def generate_metadata(
        self, generation_time: str, base_digest: bytes
    ) -> Tuple[dict, dict]:
        """Generate the ROCK's metadata (both the OCI annotation and internal metadata.

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

        annotations = {
            "org.opencontainers.image.version": self.version,
            "org.opencontainers.image.title": self.title,
            "org.opencontainers.image.ref.name": self.name,
            "org.opencontainers.image.licenses": self.rock_license,
            "org.opencontainers.image.created": generation_time,
            "org.opencontainers.image.base.digest": base_digest.hex(),
        }

        return (annotations, metadata)

    def get_build_plan(self) -> List[BuildInfo]:
        """Obtain the list of architectures and bases from the project file."""
        build_infos: List[BuildInfo] = []
        base = self.effective_base

        for platform_entry, platform in self.platforms.items():
            for build_for in platform.get("build_for") or [platform_entry]:
                for build_on in platform.get("build_on") or [platform_entry]:
                    build_infos.append(
                        BuildInfo(
                            platform=platform_entry,
                            build_on=build_on,
                            build_for=build_for,
                            base=base,
                        )
                    )

        return build_infos


def _format_pydantic_errors(
    errors: List["ErrorDict"],
    *,
    file_name: str = "rockcraft.yaml",
    base_location: Optional[str] = None,
) -> str:
    """Format errors.

    Example 1: Single error.

    Bad rockcraft.yaml content:
    - field: <some field>
      reason: <some reason>

    Example 2: Multiple errors.

    Bad rockcraft.yaml content:
    - field: <some field>
      reason: <some reason>
    - field: <some field 2>
      reason: <some reason 2>
    """
    combined = [f"Bad {file_name} content:"]
    for error in errors:
        if base_location:
            error_loc: List[Union[int, str]] = [base_location]
        else:
            error_loc = []
        error_loc.extend(error["loc"])
        formatted_loc = _format_pydantic_error_location(error_loc)
        formatted_msg = _format_pydantic_error_message(error["msg"])

        if formatted_msg == "field required":
            field_name, location = _printable_field_location_split(formatted_loc)
            combined.append(
                f"- field {field_name} required in {location} configuration"
            )
        elif formatted_msg == "extra fields not permitted":
            field_name, location = _printable_field_location_split(formatted_loc)
            combined.append(
                f"- extra field {field_name} not permitted in {location} configuration"
            )
        else:
            combined.append(f"- {formatted_msg} in field {formatted_loc!r}")

    return "\n".join(combined)


def _format_pydantic_error_location(loc: Sequence[Union[str, int]]) -> str:
    """Format location."""
    loc_parts = []
    for loc_part in loc:
        if isinstance(loc_part, str):
            loc_parts.append(loc_part)
        elif isinstance(loc_part, int):
            # Integer indicates an index. Go
            # back and fix up previous part.
            previous_part = loc_parts.pop()
            previous_part += f"[{loc_part}]"
            loc_parts.append(previous_part)
        else:
            raise RuntimeError(f"unhandled loc: {loc_part}")

    new_loc = ".".join(loc_parts)

    # Filter out internal __root__ detail.
    new_loc = new_loc.replace(".__root__", "")
    return new_loc


def _format_pydantic_error_message(msg: str) -> str:
    """Format pydantic's error message field."""
    # Replace shorthand "str" with "string".
    msg = msg.replace("str type expected", "string type expected")
    return msg


def _printable_field_location_split(location: str) -> Tuple[str, str]:
    """Return split field location.

    If top-level, location is returned as unquoted "top-level".
    If not top-level, location is returned as quoted location, e.g.

    (1) field1[idx].foo => 'foo', 'field1[idx]'
    (2) field2 => 'field2', top-level

    :returns: Tuple of <field name>, <location> as printable representations.
    """
    loc_split = location.split(".")
    field_name = repr(loc_split.pop())

    if loc_split:
        return field_name, repr(".".join(loc_split))

    return field_name, "top-level"


def load_project(filename: Path) -> Dict[str, Any]:
    """Load and unmarshal the project YAML file.

    :param filename: The YAML file to load.

    :returns: The populated project data.

    :raises ProjectLoadError: If loading fails.
    :raises ProjectValidationError: If data validation fails.
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


def transform_yaml(project_root: Path, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    """Do Rockcraft-specific transformations on a project yaml.

    :param project_root: The path that contains the "rockcraft.yaml" file.
    :param yaml_data: The data dict loaded from the yaml file.
    """
    yaml_data = apply_extensions(project_root, yaml_data)

    _add_pebble_data(yaml_data)

    return yaml_data


def _add_pebble_data(yaml_data: Dict[str, Any]) -> None:
    """Add pebble-specific contents to YAML-loaded data.

    This function adds a special "pebble" part to a project's specification, to be
    (eventually) used as the image's entrypoint.

    :param yaml_data: The project spec loaded from "rockcraft.yaml".
    :raises ProjectValidationError: If `yaml_data` already contains a "pebble" part.
    """
    if "parts" not in yaml_data:
        # Invalid project: let it return to fail in the regular validation flow.
        return

    parts = yaml_data["parts"]
    if "pebble" in parts:
        # Project already has a pebble part: this is not supported.
        raise ProjectValidationError('Cannot override the default "pebble" part')

    parts["pebble"] = Pebble.PEBBLE_PART_SPEC
