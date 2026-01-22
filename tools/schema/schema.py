#!/usr/bin/env python3
#
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2024 Canonical Ltd.
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

"""Creation of schema for rockcraft.yaml."""

import json
import os
import sys
from pathlib import Path

import yaml
from craft_parts import Part
from craft_parts.plugins import plugins

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_dir, "../../"))

import rockcraft  # noqa: E402
from rockcraft.models.project import Project  # noqa: E402


def generate_project_schema() -> str:
    """Generate the schema."""
    # Render the default template with a name
    template = Path(rockcraft.__file__).parent / "templates/simple/rockcraft.yaml.j2"
    contents = template.read_text().replace("{{name}}", "my-rock-name")

    # Initiate a project with all required fields
    project = Project.unmarshal(yaml.safe_load(contents))

    # initiate the schema with the $id and $schema fields
    initial_schema = {
        "$id": "https://github.com/canonical/rockcraft/blob/main/schema/rockcraft.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
    }
    # generate the project schema
    project_schema = project.schema(by_alias=True)
    # override the generic title "Project"
    project_schema["title"] = "Rockcraft project"
    # combine both schemas
    project_schema = {**initial_schema, **project_schema}

    # tweak the platforms definition on the Project (each value can be empty)
    project_schema["properties"]["platforms"]["additionalProperties"] = {
        "oneOf": [{"type": "null"}, {"$ref": "#/$defs/Platform"}]
    }

    # tweak the Platform (build-for can be a single string)
    project_schema["$defs"]["Platform"]["properties"]["build-for"] = {
        "oneOf": [
            {
                "title": "Build-For",
                "minItems": 1,
                "uniqueItems": True,
                "type": "array",
                "items": {"type": "string"},
            },
            {"title": "Build-For", "type": "string"},
        ]
    }

    # project.schema() will define the `parts` field as an `object`
    # so we need to manually add the schema for parts by running
    # schema() on part.spec and add the outcome project schema's definitions
    part = Part(name="placeholder", data={})
    part_schema = part.spec.schema(by_alias=True)
    project_schema["properties"]["parts"]["additionalProperties"] = {
        "$ref": "#/$defs/Part"
    }
    project_schema["$defs"]["Part"] = part_schema
    project_schema["$defs"]["Permissions"] = project_schema["$defs"]["Part"]["$defs"][
        "Permissions"
    ]
    del project_schema["$defs"]["Part"]["$defs"]

    # add conditions for plugin properties fields
    project_schema["$defs"]["Part"]["properties"]["plugin"]["enum"] = list(
        plugins.get_registered_plugins().keys()
    )

    # remove the global additionalProperties to allow for each plugin its own
    del project_schema["$defs"]["Part"]["additionalProperties"]

    # add each plugin's property names in a conditional block
    if_array = []
    for name, cls in plugins.get_registered_plugins().items():
        plugin_schema = cls.properties_class.schema()
        properties_dict = {}
        for k, v in plugin_schema.get("properties", {}).items():
            properties_dict[k] = v
        properties_dict.update(project_schema["$defs"]["Part"]["properties"])

        # Merge plugin-specific definitions into the main schema
        if "$defs" in plugin_schema:
            project_schema["$defs"].update(plugin_schema["$defs"])

        if_array.append(
            {
                "if": {"properties": {"plugin": {"const": name}}},
                "then": {
                    "$comment": "common properties had to be repeated here or they would be considered invalid by the schema validator otherwise",
                    "properties": properties_dict,
                    "additionalProperties": False,
                },
            }
        )
    project_schema["$defs"]["Part"]["allOf"] = if_array

    return json.dumps(project_schema, indent=2)


if __name__ == "__main__":
    print(generate_project_schema())
