#!/usr/bin/env python3
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2021 Canonical Ltd
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


"""Lifecycle integration."""

from pathlib import Path

import yaml
from craft_cli.errors import CraftError

from .parts import PartsLifecycle, Step
from .ui import emit


def pack():
    """Pack a ROCK."""
    # XXX: replace with proper rockcraft.yaml unmarshal and validation
    try:
        with open("rockcraft.yaml", encoding="utf-8") as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
    except OSError as err:
        raise CraftError(err) from err

    parts_data = yaml_data.get("parts")
    if not parts_data:
        emit.message("No parts specified.")
        return

    # TODO: add base image retrieval

    # TODO: add base image extraction

    # TODO: pass base image to parts lifecycle

    lifecycle = PartsLifecycle(
        parts_data,
        work_dir=Path("build"),
    )
    lifecycle.run(Step.PRIME)

    # TODO: generate layer with prime contents

    # TODO: build image with new layer
