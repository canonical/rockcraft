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

import datetime
import pydantic
from pydantic import root_validator
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
    version: str
    base: Literal["ubuntu:18.04", "ubuntu:20.04"]
    build_base: Optional[str]
    entrypoint: Optional[List[str]]
    cmd: Optional[List[str]]
    env: Optional[List[Dict[str, str]]]
    # TODO: uncomment when user-defined annotations are allowed
    # annotations: Optional[List[Dict[str, str]]]
    parts: Dict[str, Any]

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        validate_assignment = True
        extra = "forbid"
        allow_mutation = False
        allow_population_by_field_name = True
        alias_generator = lambda s: s.replace("_", "-")  # noqa: E731

    @root_validator
    def build_annotations_map(cls, values: Dict[str, Any]) -> Dict:
        """Gets the provided inputs and generates the 
        annotations map for the image
        """
        values['annotations'] = {
            'org.opencontainers.image.version': values['version'],
            # org.opencontainers.image.title
            # org.opencontainers.image.description
            # org.opencontainers.image.ref.name
            # org.opencontainers.image.base.digest
            'org.opencontainers.image.base.name': values['base'],
            # org.opencontainers.image.authors
            # org.opencontainers.image.url
            # org.opencontainers.image.source
            # org.opencontainers.image.revision
            # org.opencontainers.image.licenses
            # org.opencontainers.image.documentation
            # org.opencontainers.image.vendor
            # rocks.ubuntu.image.support.end-of-life
            # rocks.ubuntu.image.support.end-of-support
            # rocks.ubuntu.image.support.info
            'org.opencontainers.image.created': datetime.datetime.now(datetime.timezone.utc).isoformat()
            # rocks.ubuntu.image.pebble.server.version
            # rocks.ubuntu.image.pebble.client.version
        }
        
    @pydantic.validator("build_base", always=True)
    @classmethod
    def _validate_build_base(cls, build_base, values):
        """Build-base defaults to the base value if not specified."""
        if not build_base:
            build_base = values.get("base")
        return build_base

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
