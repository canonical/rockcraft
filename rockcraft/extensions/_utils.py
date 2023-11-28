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

"""Extension application helpers."""

import copy
from pathlib import Path
from typing import Any, cast

from .extension import Extension
from .registry import get_extension_class


def apply_extensions(project_root: Path, yaml_data: dict[str, Any]) -> dict[str, Any]:
    """Apply all extensions.

    :param dict yaml_data: Loaded, unprocessed rockcraft.yaml
    :returns: Modified rockcraft.yaml data with extensions applied
    """
    # Don't modify the dict passed in
    yaml_data = copy.deepcopy(yaml_data)
    declared_extensions: list[str] = cast(list[str], yaml_data.get("extensions", []))
    if not declared_extensions:
        return yaml_data

    del yaml_data["extensions"]

    # Process extensions in a consistent order
    for extension_name in sorted(declared_extensions):
        extension_class = get_extension_class(extension_name)
        extension = extension_class(
            project_root=project_root, yaml_data=copy.deepcopy(yaml_data)
        )
        extension.validate(extension_name=extension_name)
        _apply_extension(yaml_data, extension)
    return yaml_data


def _apply_extension(
    yaml_data: dict[str, Any],
    extension: Extension,
) -> None:
    # Apply the root components of the extension (if any)
    root_extension = extension.get_root_snippet()
    for property_name, property_value in root_extension.items():
        yaml_data[property_name] = _apply_extension_property(
            yaml_data.get(property_name), property_value
        )

    # Next, apply the part-specific components
    part_extension = extension.get_part_snippet()
    if "parts" not in yaml_data:
        yaml_data["parts"] = {}

    parts = yaml_data["parts"]
    for part_definition in parts.values():
        for property_name, property_value in part_extension.items():
            part_definition[property_name] = _apply_extension_property(
                part_definition.get(property_name), property_value
            )

    # Finally, add any parts specified in the extension
    parts_snippet = extension.get_parts_snippet()
    parts_names = (pn for pn in parts_snippet if pn not in yaml_data["parts"])
    for part_name in parts_names:
        parts[part_name] = parts_snippet[part_name]


def _apply_extension_property(existing_property: Any, extension_property: Any) -> Any:
    if existing_property:
        # If the property is not scalar, merge them
        if isinstance(existing_property, list) and isinstance(extension_property, list):
            merged = extension_property + existing_property

            # If the lists are just strings, remove duplicates.
            if all(isinstance(item, str) for item in merged):
                return _remove_list_duplicates(merged)

            return merged

        if isinstance(existing_property, dict) and isinstance(extension_property, dict):
            for key, value in extension_property.items():
                existing_property[key] = _apply_extension_property(
                    existing_property.get(key), value
                )
            return existing_property
        return existing_property

    return extension_property


def _remove_list_duplicates(seq: list[str]) -> list[str]:
    """De-dupe string list maintaining ordering."""
    seen: set[str] = set()
    deduped: list[str] = []

    for item in seq:
        if item not in seen:
            seen.add(item)
            deduped.append(item)

    return deduped
