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

"""Fake Extensions for use in tests."""
from typing import Any

from craft_application import util
from overrides import override
from rockcraft.extensions.extension import Extension


class FakeExtension(Extension):
    """A fake test Extension"""

    NAME = "fake-extension"

    @staticmethod
    def get_supported_bases() -> tuple[str, ...]:
        """Return a tuple of supported bases."""
        return ("ubuntu@22.04",)

    @staticmethod
    def is_experimental(base: str | None) -> bool:
        """Return whether or not this extension is unstable for given base."""
        return False

    def get_root_snippet(self) -> dict[str, Any]:
        """Return the root snippet to apply."""
        return {}

    def get_part_snippet(self) -> dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}

    def get_parts_snippet(self) -> dict[str, Any]:
        """Return the parts to add to parts."""
        return {}


class ExperimentalExtension(FakeExtension):
    """A fake test Extension that is experimental"""

    NAME = "experimental-extension"

    @staticmethod
    def get_supported_bases() -> tuple[str, ...]:
        """Return a tuple of supported bases."""
        return ("ubuntu@22.04", "ubuntu@20.04")

    @staticmethod
    def is_experimental(base: str | None) -> bool:
        return True


class InvalidPartExtension(FakeExtension):
    """A fake test Extension that has invalid parts snippet"""

    NAME = "invalid-extension"

    @override
    def get_parts_snippet(self) -> dict[str, Any]:
        return {"bad-name": {"plugin": "dump", "source": None}}


class FullExtension(FakeExtension):
    """A fake test Extension that has complete behavior"""

    NAME = "full-extension"

    @override
    def get_root_snippet(self) -> dict[str, Any]:
        """Return the root snippet to apply."""
        return {
            "services": {
                "full-extension-service": {
                    "command": "fake command",
                    "override": "replace",
                }
            }
        }

    @override
    def get_part_snippet(self) -> dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {"stage-packages": ["new-package-1"]}

    @override
    def get_parts_snippet(self) -> dict[str, Any]:
        """Return the parts to add to parts."""
        return {"full-extension/new-part": {"plugin": "nil", "source": None}}


FULL_EXTENSION_PROJECT = {
    "name": "project-with-extensions",
    "version": "latest",
    "base": "ubuntu@22.04",
    "summary": "Project with extensions",
    "description": "Project with extensions",
    "license": "Apache-2.0",
    "platforms": {"amd64": None},
    "extensions": [FullExtension.NAME],
    "parts": {"foo": {"plugin": "nil", "stage-packages": ["old-package"]}},
    "services": {
        "my-service": {
            "command": "foo",
            "override": "merge",
        }
    },
}


FULL_EXTENSION_YAML = util.dump_yaml(FULL_EXTENSION_PROJECT)
