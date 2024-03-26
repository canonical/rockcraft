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

import yaml
from craft_parts import Part

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_dir, "../../"))

from rockcraft import cli  # noqa: E402
from rockcraft.models.project import Project  # noqa: E402


def generate_project_schema() -> str:
    """Generate the schema."""

    # Initialize the default template with a name
    context = {
        "name": "my-rock-name",
    }
    # pylint: disable=W0212
    init_template = cli.commands.InitCommand._INIT_TEMPLATES[
        cli.commands.InitCommand._DEFAULT_PROFILE
    ].format(**context)

    # Initiate a project with all required fields
    project = Project.unmarshal(yaml.safe_load(init_template))

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

    # project.schema() will define the `parts` field as an `object`
    # so we need to manually add the schema for parts by running
    # schema() on part.spec and add the outcome project schema's definitions
    part = Part(name="placeholder", data={})
    part_schema = part.spec.schema(by_alias=True)
    project_schema["properties"]["parts"]["additionalProperties"] = {
        "$ref": "#/definitions/Part"
    }
    project_schema["definitions"]["Part"] = part_schema
    project_schema["definitions"]["Permissions"] = project_schema["definitions"][
        "Part"
    ]["definitions"]["Permissions"]
    del project_schema["definitions"]["Part"]["definitions"]

    return json.dumps(project_schema, indent=2)


if __name__ == "__main__":
    print(generate_project_schema())
