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
import argparse
import copy
import re
import textwrap
from pathlib import Path

import pytest
from craft_application import errors, util
from rockcraft import extensions
from rockcraft.commands import ExpandExtensionsCommand

from tests.unit.testing.extensions import (
    FULL_EXTENSION_PROJECT,
    FULL_EXTENSION_YAML,
    FullExtension,
)

# The project with the extension (FullExtension) expanded
EXPECTED_EXPAND_EXTENSIONS = textwrap.dedent(
    """\
    name: project-with-extensions
    title: project-with-extensions
    version: latest
    summary: Project with extensions
    description: Project with extensions
    base: ubuntu@22.04
    platforms:
      amd64:
        build-on:
        - amd64
        build-for:
        - amd64
    license: Apache-2.0
    parts:
      foo:
        plugin: nil
        stage-packages:
        - new-package-1
        - old-package
      full-extension/new-part:
        plugin: nil
        source: null
    services:
      my-service:
        override: merge
        command: foo
      full-extension-service:
        override: replace
        command: fake command
    """
)


@pytest.fixture
def setup_extensions(mock_extensions):
    extensions.register(FullExtension.NAME, FullExtension)


@pytest.mark.usefixtures("tmp_path", "setup_extensions")
def test_expand_extensions(emitter, fake_app_config):
    # ExpandExtensionsCommand loads "rockcraft.yaml" on the cwd
    project_file = Path("rockcraft.yaml")
    project_file.write_text(FULL_EXTENSION_YAML)

    cmd = ExpandExtensionsCommand(fake_app_config)
    cmd.run(argparse.Namespace())

    emitter.assert_message(EXPECTED_EXPAND_EXTENSIONS)


@pytest.mark.usefixtures("tmp_path", "setup_extensions")
def test_expand_extensions_error(fake_app_config):
    wrong_yaml = copy.deepcopy(FULL_EXTENSION_PROJECT)

    # Misconfigure the plugin
    wrong_yaml["parts"]["foo"]["plugin"] = "nonexistent"

    # Misconfigure a service
    wrong_yaml["services"]["my-service"]["override"] = "invalid"

    project_file = Path("rockcraft.yaml")
    dumped = util.dump_yaml(wrong_yaml)
    project_file.write_text(dumped)

    expected_message = re.escape(
        "Bad rockcraft.yaml content:\n"
        "- plugin not registered: 'nonexistent' (in field 'parts.foo')\n"
        "- input should be 'merge' or 'replace' (in field 'services.my-service.override')"
    )

    cmd = ExpandExtensionsCommand(fake_app_config)
    with pytest.raises(errors.CraftValidationError, match=expected_message):
        cmd.run(argparse.Namespace())
