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
"""Architecture definitions and conversions for Debian and Go/Docker."""

import dataclasses


@dataclasses.dataclass(frozen=True)
class ArchitectureMapping:
    """Mapping of a Debian arch to Go arch/variant (for use with registries).

    The Go-related values must conform to:
    https://github.com/opencontainers/image-spec/blob/67d2d5658fe0476ab9bf414cec164077ebff3920/config.md#properties
    """

    description: str
    go_arch: str
    go_variant: str | None = None


# The keys are valid debian architectures.
SUPPORTED_ARCHS: dict[str, ArchitectureMapping] = {
    "amd64": ArchitectureMapping(
        description="Intel 64",
        go_arch="amd64",
    ),
    "armhf": ArchitectureMapping(
        description="ARM 32-bit", go_arch="arm", go_variant="v7"
    ),
    "arm64": ArchitectureMapping(
        description="ARM 64-bit", go_arch="arm64", go_variant="v8"
    ),
    "i386": ArchitectureMapping(
        description="Intel 386",
        go_arch="386",
    ),
    "ppc64el": ArchitectureMapping(
        description="PowerPC 64-bit",
        go_arch="ppc64le",
    ),
    "riscv64": ArchitectureMapping(
        description="RISCV 64-bit",
        go_arch="riscv64",
    ),
    "s390x": ArchitectureMapping(
        description="IBM Z 64-bit",
        go_arch="s390x",
    ),
}
