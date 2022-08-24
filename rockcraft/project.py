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

from typing import Any, Dict, List, Literal, Optional, Tuple

import pydantic
import spdx_license_list  # type: ignore
import yaml
from craft_cli.errors import CraftError

from rockcraft.parts import validate_part


class ProjectLoadError(CraftError):
    """Error loading rockcraft.yaml."""


class ProjectValidationError(CraftError):
    """Error validatiing rockcraft.yaml."""


class Project(pydantic.BaseModel):
    """Rockcraft project definition."""

    name: str
    title: Optional[str]
    summary: str
    description: str
    rock_license: str = pydantic.Field(alias="license")
    version: str
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

    @pydantic.validator("parts", pre=True)
    @classmethod
    def _add_pebble_part(cls, parts):
        """Force pebble part to ensure Pebble is always installed."""
        # TODO: by adding this part at this stage, if there is an error
        # with it, a custom ProjectValidationError exception will be thrown,
        # with the message "Bad rockcraft.yaml content", which is misleading
        # since the user hasn't specified such part.
        # Is there another logical place where this insertion could happen?
        pebble_part_spec = {
            "pebble": {
                "plugin": "go",
                "source": "https://github.com/canonical/pebble.git",
                "build-environment": [
                    {"CGO_ENABLED": "0"},
                ],
                "build-snaps": ["go"],
                "prime": ["bin/pebble"]
            }
        }
        parts = {**pebble_part_spec, **parts}
        return parts

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
            raise TypeError("part data is not a dictionary")

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
