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

import pytest
import yaml

import tests
from rockcraft.pebble import Pebble
from rockcraft.project import Service


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
                        "mockServiceOne": Service(  # type: ignore
                            override="replace",
                            command="foo",
                            on_success="shutdown",
                        ).dict(exclude_none=True, by_alias=True)
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
                    "    on-success: shutdown"
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
        check,
        tmp_path,
        existing_layers,
        expected_new_layer_prefix,
        layer_content,
        expected_layer_yaml,
    ):
        # Mock the base layer dir just to test the detection of existing
        # Pebble layers
        mock_base_layer_dir = tmp_path / "base"
        tmp_base_layer_dir = mock_base_layer_dir / "var/lib/pebble/default/layers/"
        tmp_base_layer_dir.mkdir(parents=True)
        for layer in existing_layers:
            (tmp_base_layer_dir / layer).touch()

        pebble_obj = Pebble()
        pebble_obj.define_pebble_layer(
            tmp_path,
            mock_base_layer_dir,
            layer_content,
            "my-rock",
        )

        out_pebble_layer = str(
            f"{tmp_path}/{pebble_obj.PEBBLE_LAYERS_PATH}/"
            f"{expected_new_layer_prefix}-my-rock.yaml"
        )
        check.is_true(os.path.exists(out_pebble_layer))
        check.equal(oct((tmp_path / pebble_obj.PEBBLE_PATH).stat().st_mode)[-3:], "777")
        check.equal(
            oct(Path(out_pebble_layer).stat().st_mode)[-3:],
            "777",
        )
        with open(out_pebble_layer) as f:
            content = f.read()
            check.equal(content, expected_layer_yaml)
            content = yaml.safe_load(content)
            for service_fields in content["services"].values():
                for field in service_fields:
                    check.is_not_in("_", field)
