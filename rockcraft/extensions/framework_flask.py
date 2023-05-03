# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2022 Canonical Ltd.
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

"""Generic GNOME extension to support core22 and onwards."""

import subprocess
from textwrap import dedent
from typing import Any, Dict, List, Optional, Tuple

from overrides import overrides

from .extension import Extension, get_extensions_data_dir, prepend_to_env


class FrameworkFlask(Extension):
    """An extension that eases the creation of ROCKS that integrate with Flask."""

    @staticmethod
    @overrides
    def get_supported_bases() -> Tuple[str, ...]:
        return ("ubuntu:22.04",)

    @staticmethod
    @overrides
    def is_experimental(base: Optional[str]) -> bool:
        return False

    @overrides
    def get_part_snippet(self) -> Dict[str, Any]:
        return {}

    @overrides
    def get_root_snippet(self) -> Dict[str, Any]:
        if "services" not in self.yaml_data:
            snippet: Dict[str, Any] = {
                "services": {
                    "flask": {
                        "override": "replace",
                        "command": "flask run --host=0.0.0.0",
                        "startup": "disabled",
                        "environment": {
                            "SECRET_KEY": "replaceme",
                            "FLASK_APP": "/srv/webapp/app",
                        },
                    },
                    "flask-debug": {
                        "override": "replace",
                        "command": "flask run --host=0.0.0.0",
                        "startup": "disabled",
                        "environment": {
                            "SECRET_KEY": "replaceme",
                            "FLASK_APP": "/srv/webapp/app",
                            "FLASK_ENV": "development",
                        },
                    },
                }
            }
        else:
            snippet: Dict[str, Any] = {}

        if "version" not in self.yaml_data:
            git_version = "1.0"
            # subprocess.check_output(
            #     ["git", "describe", "--tags", "--always", "--dirty"],
            # )
            snippet["version"] = f"git+{git_version}"
        if "summary" not in self.yaml_data:
            snippet["summary"] = "OCI Image for a Flask Application"
        if "description" not in self.yaml_data:
            snippet["description"] = dedent(
                """\
                This image is meant to be used with a charm. It can be used standalone following the
                ROCKs conventions for execution. It defines two pebble services:

                - flask
                - flask-debug

                The SECRET_KEY has a default, but should be changed on deployment.

                The assets are expected on /srv/webapp and the app is expected to be found in
                /srv/webapp/app.
            """
            )
        if "base" not in self.yaml_data:
            snippet["base"] = "ubuntu:22.04"
        if "platforms" not in self.yaml_data:
            snippet["platforms"] = {"amd64": {}}
        if "license" not in self.yaml_data:
            snippet["license"] = "proprietary"
        return snippet

    @overrides
    def get_parts_snippet(self) -> Dict[str, Any]:
        snippet = {
            "flask": {
                "source": ".",
                "plugin": "python",
                "stage-packages": ["python3-venv"],
            },
            "contents": {
                "source": ".",
                "plugin": "dump",
                "build-snaps": ["node/18/stable"],
                "override-build": dedent(
                    """\
                        yarn install --production
                        yarn run build
                        craftctl default
                    """
                ),
                "organize": {"*": "srv/"},
                "stage": [
                    "srv/templates",
                    "srv/static",
                    "srv/webapp",
                ],
            },
        }

        if (self.project_root / "requirements.txt").exists():
            snippet["flask"]["python-requirements"] = ["requirements.txt"]
        else:
            snippet["flask"]["python-packages"] = ["Flask"]

        return snippet
