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
import textwrap
from typing import Any, Dict, Optional, Tuple

import pytest
from overrides import override

from rockcraft import errors, extensions
from rockcraft.extensions.extension import Extension
from rockcraft.project import load_project


class FakeExtension(Extension):
    """A fake test Extension"""

    NAME = "fake-extension"

    @staticmethod
    def get_supported_bases() -> Tuple[str, ...]:
        """Return a tuple of supported bases."""
        return ("ubuntu:22.04",)

    @staticmethod
    def is_experimental(base: Optional[str]) -> bool:
        """Return whether or not this extension is unstable for given base."""
        return False

    def get_root_snippet(self) -> Dict[str, Any]:
        """Return the root snippet to apply."""
        return {}

    def get_part_snippet(self) -> Dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {}

    def get_parts_snippet(self) -> Dict[str, Any]:
        """Return the parts to add to parts."""
        return {}


class ExperimentalExtension(FakeExtension):
    """A fake test Extension that is experimental"""

    NAME = "experimental-extension"

    @staticmethod
    def is_experimental(base: Optional[str]) -> bool:
        return True


class InvalidPartExtension(FakeExtension):
    """A fake test Extension that has invalid parts snippet"""

    NAME = "invalid-extension"

    @override
    def get_parts_snippet(self) -> Dict[str, Any]:
        return {"bad-name": {"plugin": "dump", "source": None}}


class FullExtension(FakeExtension):
    """A fake test Extension that has complete behavior"""

    NAME = "full-extension"

    @override
    def get_root_snippet(self) -> Dict[str, Any]:
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
    def get_part_snippet(self) -> Dict[str, Any]:
        """Return the part snippet to apply to existing parts."""
        return {"stage-packages": ["new-package-1"]}

    @override
    def get_parts_snippet(self) -> Dict[str, Any]:
        """Return the parts to add to parts."""
        return {"full-extension/new-part": {"plugin": "nil", "source": None}}


@pytest.fixture
def fake_extensions(mock_extensions):
    extensions.register(FakeExtension.NAME, FakeExtension)
    extensions.register(ExperimentalExtension.NAME, ExperimentalExtension)
    extensions.register(InvalidPartExtension.NAME, InvalidPartExtension)
    extensions.register(FullExtension.NAME, FullExtension)


@pytest.fixture
def input_yaml():
    return {"base": "ubuntu:22.04"}


def test_experimental_with_env(fake_extensions, tmp_path, input_yaml, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    input_yaml["extensions"] = [ExperimentalExtension.NAME]
    project_root = tmp_path
    extensions.apply_extensions(project_root, input_yaml)


def test_experimental_no_env(fake_extensions, tmp_path, input_yaml):
    input_yaml["extensions"] = [ExperimentalExtension.NAME]
    with pytest.raises(errors.ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)

    expected_message = f"Extension is experimental: '{ExperimentalExtension.NAME}'"
    assert str(exc.value) == expected_message


@pytest.mark.parametrize("base", ("ubuntu:20.04", "bare"))
def test_wrong_base(fake_extensions, tmp_path, input_yaml, base):
    input_yaml["extensions"] = [FakeExtension.NAME]
    input_yaml["base"] = base
    with pytest.raises(errors.ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)

    expected_message = (
        f"Extension '{FakeExtension.NAME}' does not support base: '{base}'"
    )
    assert str(exc.value) == expected_message


def test_invalid_parts(fake_extensions, tmp_path, input_yaml):
    input_yaml["extensions"] = [InvalidPartExtension.NAME]

    with pytest.raises(ValueError) as exc:
        extensions.apply_extensions(tmp_path, input_yaml)

    assert "Extension has invalid part names" in str(exc.value)


def test_apply_extensions(fake_extensions, tmp_path, input_yaml):
    input_yaml["services"] = {"my-service": {"command": "foo", "override": "merge"}}
    input_yaml["extensions"] = [FullExtension.NAME]
    input_yaml["parts"] = {
        "my-part": {"plugin": "nil", "source": None, "stage-packages": ["old-package"]}
    }

    applied = extensions.apply_extensions(tmp_path, input_yaml)

    # Root snippet extends the project's
    services = applied["services"]
    assert services["my-service"] == {
        "command": "foo",
        "override": "merge",
    }
    assert services["full-extension-service"] == {
        "command": "fake command",
        "override": "replace",
    }

    # Part snippet extends the existing part
    parts = applied["parts"]
    assert parts["my-part"]["stage-packages"] == [
        "new-package-1",
        "old-package",
    ]

    # New part
    assert parts[f"{FullExtension.NAME}/new-part"] == {"plugin": "nil", "source": None}


def test_project_load_extensions(fake_extensions, tmp_path):
    """Test that load_project() correctly applies the extensions."""
    yaml_data = textwrap.dedent(
        f"""
        name: project-with-extensions
        version: latest
        base: ubuntu:22.04
        summary: Project with extensions
        description: Project with extensions
        license: Apache-2.0
        platforms:
            amd64:

        extensions:
            - {FullExtension.NAME}

        parts:
            foo:
                plugin: nil
                stage-packages:
                    - old-package

        services:
            my-service:
                command: foo
                override: merge
    """
    )
    rockcraft_yaml = tmp_path / "rockcraft.yaml"
    rockcraft_yaml.write_text(yaml_data)

    project = load_project(rockcraft_yaml)

    # Root snippet extends the project's
    services = project.services
    assert services is not None
    assert len(services) == 2
    assert services["full-extension-service"].command == "fake command"
    assert services["full-extension-service"].override == "replace"
    assert services["my-service"].command == "foo"
    assert services["my-service"].override == "merge"

    # Part snippet extends the existing part
    parts = project.parts
    assert parts["foo"]["stage-packages"] == [
        "new-package-1",
        "old-package",
    ]

    # New part
    assert parts[f"{FullExtension.NAME}/new-part"] == {"plugin": "nil", "source": None}
