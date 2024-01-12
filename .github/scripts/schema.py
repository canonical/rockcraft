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
import sys
from typing import TYPE_CHECKING

from craft_parts import Part

sys.path.append("rockcraft")

from rockcraft import errors  # noqa: E402
from rockcraft.models.project import Project  # noqa: E402

if TYPE_CHECKING:
    import argparse


def generate_project_schema() -> str:
    """Generate the schema."""
    project = Project(
        name="placeholder",
        version="1.0",
        summary="summary",
        description="description",
        base="ubuntu@22.04",
        parts=[],
        license="MIT",
        platforms={"amd64": None},
    )
    project_schema = project.schema(by_alias=True)

    part = Part(name="placeholder", data={})
    part_schema = part.spec.schema(by_alias=True)

    project_schema["properties"]["parts"]["additionalProperties"] = {
        "$ref": "#/definitions/Part"
    }
    project_schema["definitions"]["Part"] = part_schema

    return json.dumps(project_schema, indent=2)


if __name__ == "__main__":
    print(generate_project_schema())
