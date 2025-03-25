#  This file is part of Rockcraft.
#
#  Copyright 2023 Canonical Ltd.
#
#  This program is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License version 3, as
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
#  SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Project-related utility functions for testing."""

from rockcraft.models import Project


def create_project(**kwargs) -> Project:
    """Utility function to create test Projects with defaults."""
    base = kwargs.get("base", "ubuntu@22.04")

    build_base = kwargs.get("build_base")
    if not build_base:
        build_base = base if base != "bare" else "ubuntu@22.04"

    return Project.unmarshal(
        {
            "name": kwargs.get("name", "default"),
            "version": kwargs.get("version", "1.0"),
            "summary": kwargs.get("summary", "default project"),
            "description": kwargs.get("description", "default project"),
            "base": base,
            "build-base": build_base,
            "parts": kwargs.get("parts", {}),
            "license": kwargs.get("license", "MIT"),
            "platforms": kwargs.get("platforms", {"amd64": None}),
            "package-repositories": kwargs.get("package_repositories"),
        }
    )
