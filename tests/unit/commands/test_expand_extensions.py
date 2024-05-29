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
import textwrap
from pathlib import Path

import pytest

from rockcraft import extensions
from rockcraft.commands import ExpandExtensionsCommand
from tests.unit.testing.extensions import FULL_EXTENSION_YAML, FullExtension

# The project with the extension (FullExtension) expanded
EXPECTED_EXPAND_EXTENSIONS = textwrap.dedent(
    """\
    name: project-with-extensions
    title: project-with-extensions
    version: latest
    summary: Project with extensions
    description: Project with extensions
    base: ubuntu@22.04
    build-base: ubuntu@22.04
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
      pebble:
        plugin: nil
        stage-snaps:
        - pebble/latest/stable
        override-prime: |-
          craftctl default
          mkdir -p var/lib/pebble/default/layers
          chmod 777 var/lib/pebble/default
        stage:
        - bin/pebble
    services:
      my-service:
        override: merge
        command: foo
      full-extension-service:
        override: replace
        command: fake command
    """
)


@pytest.fixture()
def setup_extensions(mock_extensions):
    extensions.register(FullExtension.NAME, FullExtension)


def test_expand_extensions(setup_extensions, emitter, new_dir):
    # ExpandExtensionsCommand loads "rockcraft.yaml" on the cwd
    project_file = Path("rockcraft.yaml")
    project_file.write_text(FULL_EXTENSION_YAML)

    cmd = ExpandExtensionsCommand(None)
    cmd.run(argparse.Namespace())

    emitter.assert_message(EXPECTED_EXPAND_EXTENSIONS)
