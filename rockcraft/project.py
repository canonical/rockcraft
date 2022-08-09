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

import operator
import platform
from functools import reduce
from typing import Any, Dict, List, Literal, Optional, Tuple

import pydantic
import spdx_license_list  # type: ignore
import yaml
from craft_cli.errors import CraftError

from rockcraft.parts import validate_part

_SELF_UTS_MACHINE = platform.machine().lower()


class ProjectLoadError(CraftError):
    """Error loading rockcraft.yaml."""


class ProjectValidationError(CraftError):
    """Error validatiing rockcraft.yaml."""


class ArchitectureMapping(pydantic.BaseModel):
    """Maps different denominations of the same architecture."""

    description: str
    deb_arch: str
    compatible_uts_machine_archs: List[str]
    go_arch: str


_SUPPORTED_ARCHS: Dict[str, ArchitectureMapping] = {
    "amd64": ArchitectureMapping(
        description="Intel 64",
        deb_arch="amd64",
        compatible_uts_machine_archs=["x86_64"],
        go_arch="amd64",
    ),
    "arm": ArchitectureMapping(
        description="ARM 32-bit",
        deb_arch="armhf",
        compatible_uts_machine_archs=["arm"],
        go_arch="arm",
    ),
    "arm64": ArchitectureMapping(
        description="ARM 64-bit",
        deb_arch="arm64",
        compatible_uts_machine_archs=["aarch64"],
        go_arch="arm64",
    ),
    "i386": ArchitectureMapping(
        description="Intel 386",
        deb_arch="i386",
        compatible_uts_machine_archs=["i386"],  # TODO: also include "i686", "x86_64"?
        go_arch="386",
    ),
    "ppc64le": ArchitectureMapping(
        description="PowerPC 64-bit",
        deb_arch="ppc64el",
        compatible_uts_machine_archs=["ppc64le"],
        go_arch="ppc64le",
    ),
    "riscv64": ArchitectureMapping(
        description="RISCV 64-bit",
        deb_arch="riscv64",
        compatible_uts_machine_archs=["riscv64"],
        go_arch="riscv64",
    ),
    "s390x": ArchitectureMapping(
        description="IBM Z 64-bit",
        deb_arch="s390x",
        compatible_uts_machine_archs=["s390x"],
        go_arch="s390x",
    ),
}


class Platform(pydantic.BaseModel):
    """Rockcraft project platform definition."""

    build_on: Optional[  # type: ignore
        pydantic.conlist(str, unique_items=True, min_items=1)  # type: ignore
    ] = pydantic.Field(alias="build-on")
    build_for: Optional[  # type: ignore
        pydantic.conlist(str, unique_items=True, min_items=1)  # type: ignore
    ] = pydantic.Field(alias="build-for")

    @pydantic.validator("build_for", pre=True)
    @classmethod
    def _vectorise_build_for(cls, val):
        """Vectorise target architecture if needed."""
        if isinstance(val, str):
            val = [val]
        return val

    @pydantic.root_validator(skip_on_failure=True)
    @classmethod
    def _validate_platform_set(cls, values):
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


class Project(pydantic.BaseModel):
    """Rockcraft project definition."""

    name: str
    title: Optional[str]
    summary: str
    description: str
    rock_license: str = pydantic.Field(alias="license")
    version: str
    platforms: Dict[str, Any]
    base: Literal["bare", "ubuntu:18.04", "ubuntu:20.04", "ubuntu:22.04"]
    build_base: Optional[
        Literal["ubuntu:18.04", "ubuntu:20.04", "ubuntu:22.04"]
    ] = pydantic.Field(alias="build-base")
    entrypoint: Optional[List[str]]
    cmd: Optional[List[str]]
    env: Optional[List[Dict[str, str]]]

    parts: Dict[str, Any]

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        validate_assignment = True
        extra = "forbid"
        allow_mutation = False
        allow_population_by_field_name = True
        alias_generator = lambda s: s.replace("_", "-")  # noqa: E731

    @pydantic.validator("rock_license", always=True)
    @classmethod
    def _validate_license(cls, rock_license):
        """Make sure the provided license is valid and in SPDX format."""
        if rock_license.lower() not in [
            lic.lower() for lic in spdx_license_list.LICENSES
        ]:
            raise ProjectValidationError(
                f"License {rock_license} not valid. It must be valid and in SPDX format."
            )
        return next(
            lic
            for lic in spdx_license_list.LICENSES
            if rock_license.lower() == lic.lower()
        )

    @pydantic.validator("title", always=True)
    @classmethod
    def _validate_title(cls, title, values):
        """If title is not provided, it default to the provided ROCK name."""
        if not title:
            title = values["name"]
        return title

    @pydantic.validator("build_base", always=True)
    @classmethod
    def _validate_build_base(cls, build_base, values):
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
        return build_base

    @pydantic.validator("platforms")
    @classmethod
    def _validate_all_platforms(cls, platforms):
        """Make sure all provided platforms are tangible and sane."""
        for platform_label in platforms:
            platform = platforms[platform_label] if platforms[platform_label] else {}
            error_prefix = f"Error for platform entry '{platform_label}'"

            # Make sure the provided platform_set is valid
            platform = Platform(**platform).dict()

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
                if (
                    platform_label in _SUPPORTED_ARCHS
                    and platform_label != build_target
                ):
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
            if not any(b_o in _SUPPORTED_ARCHS for b_o in build_on_one_of):
                raise ProjectValidationError(
                    str(
                        f"{error_prefix}: trying to build ROCK in one of "
                        f"{build_on_one_of}, but none of these build architectures is supported. "
                        f"Supported architectures: {list(_SUPPORTED_ARCHS.keys())}"
                    )
                )

            if build_target not in _SUPPORTED_ARCHS:
                raise ProjectValidationError(
                    str(
                        f"{error_prefix}: trying to build ROCK for target "
                        f"architecture {build_target}, which is not supported. "
                        f"Supported architectures: {list(_SUPPORTED_ARCHS.keys())}"
                    )
                )

            # The underlying build machine must be compatible
            # with both build_on and build_for
            # TODO: in the future, this may be removed
            # as Rockcraft gains the ability to natively build
            # for multiple architectures
            build_for_compatible_uts = _SUPPORTED_ARCHS[
                build_target
            ].compatible_uts_machine_archs
            if _SELF_UTS_MACHINE not in build_for_compatible_uts:
                raise ProjectValidationError(
                    str(
                        f"{error_prefix}: this machine's architecture ({_SELF_UTS_MACHINE}) "
                        "is not compatible with the ROCK's target architecture. Can only "
                        f"build a ROCK for {build_target} if the host is compatible with {build_for_compatible_uts}."
                    )
                )

            build_on_compatible_uts = list(
                reduce(
                    operator.add,
                    map(
                        lambda m: _SUPPORTED_ARCHS[m].compatible_uts_machine_archs,
                        build_on_one_of,
                    ),
                )
            )
            if _SELF_UTS_MACHINE not in build_on_compatible_uts:
                raise ProjectValidationError(
                    str(
                        f"{error_prefix}: this ROCK must be built on one of the "
                        f"following architectures: {build_on_compatible_uts}. "
                        f"This machine ({_SELF_UTS_MACHINE}) is not one of those."
                    )
                )

        return platforms

    @pydantic.validator("parts", each_item=True)
    @classmethod
    def _validate_parts(cls, item):
        """Verify each part (craft-parts will re-validate this)."""
        validate_part(item)
        return item

    @classmethod
    def unmarshal(cls, data: Dict[str, Any]) -> "Project":
        """Create and populate a new ``Project`` object from dictionary data.

        The unmarshal method validates entries in the input dictionary, populating
        the corresponding fields in the data object.

        :param data: The dictionary data to unmarshal.

        :return: The newly created object.

        :raise TypeError: If data is not a dictionary.
        """
        if not isinstance(data, dict):
            raise TypeError("project data is not a dictionary")

        try:
            project = Project(**data)
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


def _format_pydantic_errors(errors, *, file_name: str = "rockcraft.yaml"):
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
        formatted_loc = _format_pydantic_error_location(error["loc"])
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


def _format_pydantic_error_location(loc):
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

    loc = ".".join(loc_parts)

    # Filter out internal __root__ detail.
    loc = loc.replace(".__root__", "")
    return loc


def _format_pydantic_error_message(msg):
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


def load_project(filename: str) -> Project:
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

    return Project.unmarshal(yaml_data)
