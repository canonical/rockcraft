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

"""An experimental extension for the Flask framework."""

import copy
import posixpath
import re
from typing import Any, Dict, Optional, Tuple

from overrides import override

from ._utils import _apply_extension_property
from .extension import Extension
from ..errors import ExtensionError


class Flask(Extension):
    """An extension for constructing Python applications based on the Flask framework."""

    @staticmethod
    @override
    def get_supported_bases() -> Tuple[str, ...]:
        """Return supported bases."""
        return "bare", "ubuntu:20.04", "ubuntu:22.04"

    @staticmethod
    @override
    def is_experimental(base: Optional[str]) -> bool:
        """Check if the extension is in an experimental state."""
        return True

    @override
    def get_root_snippet(self) -> Dict[str, Any]:
        """Fill in some default root components for Flask.

        Default values:
          - run_user: _daemon_
          - build-base: ubuntu:22.04 (only if user specify bare without a build-base)
          - platform: amd64
        """
        snippet: Dict[str, Any] = {}
        if "run_user" not in self.yaml_data:
            snippet["run_user"] = "_daemon_"
        if (
            "build-base" not in self.yaml_data
            and self.yaml_data.get("base", "bare") == "bare"
        ):
            snippet["build-base"] = "ubuntu:22.04"
        if "platforms" not in self.yaml_data:
            snippet["platforms"] = {"amd64": {}}
        current_parts = copy.deepcopy(self.yaml_data.get("parts", {}))
        current_parts.update(self._gen_new_parts())
        snippet["parts"] = current_parts
        snippet["services"] = self._gen_services()
        return snippet

    def _gen_services(self):
        """Return the services snipped to be applied to the rockcraft file."""
        services = {
            "flask": {
                "override": "replace",
                "startup": "enabled",
                "command": "/bin/python3 -m gunicorn --bind 0.0.0.0:8000 app:app",
                "user": "_daemon_",
                "working-dir": "/srv/flask/app",
            }
        }
        existing_services = copy.deepcopy(self.yaml_data.get("services", {}))
        for existing_service_name, existing_service in existing_services.items():
            if existing_service_name in services:
                services[existing_service_name].update(existing_service)
            else:
                services[existing_service_name] = existing_service
        return services

    @override
    def get_part_snippet(self) -> Dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}

    def _merge_part(self, base_part: dict, new_part: dict) -> dict:
        """Merge two part definitions by the extension part merging rule."""
        result = {}
        properties = set(base_part.keys()).union(set(new_part.keys()))
        for property_name in properties:
            if property_name in base_part and property_name not in new_part:
                result[property_name] = base_part[property_name]
            elif property_name not in base_part and property_name in new_part:
                result[property_name] = new_part[property_name]
            else:
                result[property_name] = _apply_extension_property(
                    base_part[property_name], new_part[property_name]
                )
        return result

    def _merge_existing_part(self, part_name: str, part_def: dict) -> dict:
        """Merge the new part with the existing part in the current rockcraft.yaml."""
        existing_part = self.yaml_data.get("parts", {}).get(part_name, {})
        return self._merge_part(existing_part, part_def)

    def _gen_new_parts(self) -> Dict[str, Any]:
        """Generate new parts for the flask extension.

        Parts added:
            - flask/dependencies: install Python dependencies
            - flask/install-app: copy the flask project into the OCI image
        """
        if not (self.project_root / "requirements.txt").exists():
            raise ExtensionError(
                "missing requirements.txt file, "
                "flask extension requires this file with flask specified as a dependency"
            )
        source_files = [f.name for f in sorted(self.project_root.iterdir())]
        renaming_map = {f: posixpath.join("srv/flask/app", f) for f in source_files}
        install_app_part_name = "flask/install-app"
        dependencies_part_name = "flask/dependencies"

        if install_app_part_name not in self.yaml_data.get("parts", {}):
            raise ExtensionError(
                "flask extension required flask/install-app not found "
                "in parts of the rockcraft file"
            )
        install_prime = self.yaml_data.get("parts")[install_app_part_name].get("prime")
        if not install_prime:
            raise ExtensionError(
                "flask extension required prime list not found or empty"
                "in the flask/install-app part of the rockcraft file"
            )
        if not all(re.match("-? *srv/flask/app", p) for p in install_prime):
            raise ExtensionError(
                "flask extension required prime entry in the flask/install-app part"
                "to start with srv/flask/app"
            )

        # Users are required to compile any static assets prior to executing the
        # rockcraft pack command, so assets can be included in the final OCI image.
        install_app_part = {
            "plugin": "dump",
            "source": ".",
            "organize": renaming_map,
            "stage": list(renaming_map.values()),
        }
        dependencies_part = {
            "plugin": "python",
            "stage-packages": ["python3-venv"],
            "source": ".",
            "python-packages": ["gunicorn"],
            "python-requirements": ["requirements.txt"],
        }
        snippet = {
            dependencies_part_name: self._merge_existing_part(
                dependencies_part_name, dependencies_part
            ),
            install_app_part_name: self._merge_existing_part(
                install_app_part_name, install_app_part
            ),
        }
        if self.yaml_data["base"] == "bare":
            snippet["flask/container-processing"] = {
                "plugin": "nil",
                "source": ".",
                "override-build": "mkdir -m 777 ${CRAFT_PART_INSTALL}/tmp",
            }
        return snippet

    @override
    def get_parts_snippet(self) -> Dict[str, Any]:
        """Return the parts to add to parts."""
        return {}
