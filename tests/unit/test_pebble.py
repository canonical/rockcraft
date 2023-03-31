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

import os
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

import tests
from rockcraft.pebble import Pebble


@tests.linux_only
class TestPebble:
    """Pebble-specific metadata and operations."""

    def test_attributes(self):
        assert Pebble.PEBBLE_PATH == "var/lib/pebble/default"
        assert Pebble.PEBBLE_LAYERS_PATH == "var/lib/pebble/default/layers"
        assert Pebble.PEBBLE_BINARY_PATH == "bin/pebble"
        assert all(
            field in Pebble.PEBBLE_PART_SPEC
            for field in ["plugin", "stage-snaps", "stage", "override-prime"]
        )

    @pytest.mark.parametrize(
        "existing_layers,expected_new_layer_prefix,layer_content,expected_layer_yaml",
        [
            # Test Case 1:
            # Without any previous layers, the default layer prefix is 001.
            (
                [],
                "001",
                {
                    "summary": "mock summary",
                    "description": "mock description",
                    "services": {
                        "mockServiceOne": {"override": "replace", "command": "foo"}
                    },
                },
                (
                    "summary: mock summary"
                    "{n}"
                    "description: mock description"
                    "{n}"
                    "services:"
                    "{n}"
                    "  mockServiceOne:"
                    "{n}"
                    "    override: replace"
                    "{n}"
                    "    command: foo"
                    "{n}"
                ).format(n=os.linesep),
            ),
            # Test Case 2:
            # With existing layers, the default layer prefix is an increment.
            # Also make sure it works with multiple services.
            (
                ["001-existing-layer1.yml", "003-existing-layer3.yaml"],
                "004",
                {
                    "summary": "mock summary",
                    "description": "mock description",
                    "services": {
                        "mockServiceOne": {"override": "replace", "command": "foo"},
                        "mockServiceTwo": {"override": "merge", "command": "bar"},
                    },
                },
                (
                    "summary: mock summary"
                    "{n}"
                    "description: mock description"
                    "{n}"
                    "services:"
                    "{n}"
                    "  mockServiceOne:"
                    "{n}"
                    "    override: replace"
                    "{n}"
                    "    command: foo"
                    "{n}"
                    "  mockServiceTwo:"
                    "{n}"
                    "    override: merge"
                    "{n}"
                    "    command: bar"
                    "{n}"
                ).format(n=os.linesep),
            ),
            # Test Case 3:
            # If there are more files that are not layers, they are ignored.
            (
                ["2-bad-layer.yaml", "001-good-layer.yml", "not-a-layer"],
                "002",
                {
                    "summary": "mock summary",
                    "description": "mock description",
                    "services": {
                        "mockServiceOne": {"override": "replace", "command": "foo"}
                    },
                },
                (
                    "summary: mock summary"
                    "{n}"
                    "description: mock description"
                    "{n}"
                    "services:"
                    "{n}"
                    "  mockServiceOne:"
                    "{n}"
                    "    override: replace"
                    "{n}"
                    "    command: foo"
                    "{n}"
                ).format(n=os.linesep),
            ),
        ],
    )
    def test_define_pebble_layer(
        self,
        tmp_path,
        existing_layers,
        expected_new_layer_prefix,
        layer_content,
        expected_layer_yaml,
    ):
        # pylint: disable=too-many-locals
        mock_rock_name = "my-rock"

        # Mock the base layer dir just to test the detection of existing
        # Pebble layers
        mock_base_layer_dir = tmp_path / "base"
        tmp_base_layer_dir = mock_base_layer_dir / "var/lib/pebble/default/layers/"
        tmp_base_layer_dir.mkdir(parents=True)
        for layer in existing_layers:
            tmp_layer_file = tmp_base_layer_dir / layer
            tmp_layer_file.touch()

        mocked_data = {"writes": ""}

        def mock_write(s):
            mocked_data["writes"] += s

        m = mock_open()
        pebble_obj = Pebble()
        with patch("builtins.open", m) as f:
            with patch("pathlib.Path.mkdir") as local_mock_mkdir:
                m.return_value.write = mock_write
                pebble_obj.define_pebble_layer(
                    Path("fake-tmp-target-dir"),
                    mock_base_layer_dir,
                    layer_content,
                    mock_rock_name,
                )

        assert (
            f.call_args[0][0].name
            == f"{expected_new_layer_prefix}-{mock_rock_name}.yaml"
        )
        local_mock_mkdir.assert_called_once_with(parents=True)
        assert mocked_data["writes"] == expected_layer_yaml
