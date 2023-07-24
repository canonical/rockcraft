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

import pydantic
import pytest
import re
import yaml

import tests
from rockcraft.pebble import Pebble, Service


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

    def test_full_service(self):
        full_service = {
            "override": "merge",
            "command": "foo cmd",
            "summary": "mock summary",
            "description": "mock description",
            "startup": "enabled",
            "after": ["foo"],
            "before": ["bar"],
            "requires": ["some-other"],
            "environment": {"envVar": "value"},
            "user": "ubuntu",
            "user-id": 1000,
            "group": "ubuntu",
            "group-id": 1000,
            "working-dir": "/tmp",
            "on-success": "ignore",
            "on-failure": "restart",
            "on-check-failure": {"check": "restart"},
            "backoff-delay": "10ms",
            "backoff-factor": 1.2,
            "backoff-limit": "1m",
            "kill-delay": "5s",
        }
        _ = Service(**full_service)

    def test_minimal_service(self):
        _ = Service(override="merge", command="foo cmd")  # pyright: ignore

    @pytest.mark.parametrize(
        "bad_service,error",
        [
            # Missing fields
            ({}, r"^2 validation errors[\s\S]*override[\s\S]*command"),
            # Bad attributes values
            (
                {
                    "override": "bad value",
                    "command": "free text allowed",
                    "startup": "bad value",
                    "on-success": "bad value",
                    "on-failure": "bad value",
                    "on-check-failure": {"check": "bad value"},
                },
                r"^5 validation errors[\s\S]*"
                r"override[\s\S]*unexpected value[\s\S]*'merge', 'replace'[\s\S]*"
                r"startup[\s\S]*unexpected value[\s\S]*'enabled', 'disabled'[\s\S]*"
                r"on-success[\s\S]*unexpected value[\s\S]*"
                r"'restart', 'shutdown', 'ignore'[\s\S]*"
                r"on-failure[\s\S]*unexpected value[\s\S]*"
                r"'restart', 'shutdown', 'ignore'[\s\S]*"
                r"on-check-failure[\s\S]*unexpected value[\s\S]*"
                r"'restart', 'shutdown', 'ignore'[\s\S]*",
            ),
            # Bad attribute types
            (
                {
                    "override": ["merge"],
                    "command": ["not a string"],
                    "summary": {"foo": "bar"},
                    "after": "not a List",
                    "environment": "not a Dict",
                    "user-id": "not an int",
                    "on-check-failure": {"check": ["not a Literal"]},
                    "backoff-factor": "not a float",
                },
                r"^8 validation errors[\s\S]*"
                r"unhashable type[\s\S]*"
                r"str type expected[\s\S]*"
                r"value is not a valid list[\s\S]*"
                r"value is not a valid dict[\s\S]*"
                r"value is not a valid integer[\s\S]*"
                r"unhashable type[\s\S]*"
                r"value is not a valid float[\s\S]*",
            ),
        ],
    )
    def test_bad_services(self, bad_service, error):
        with pytest.raises(pydantic.ValidationError) as err:
            _ = Service(**bad_service)
        assert re.match(error, str(err.value)), "Unexpected Service validation error"
