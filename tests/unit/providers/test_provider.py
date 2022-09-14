# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021 Canonical Ltd.
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

import pytest

from rockcraft import providers

known_provider_classes = [providers.LXDProvider, providers.MultipassProvider]


@pytest.fixture(params=known_provider_classes)
def provider_class(request):
    return request.param


@pytest.mark.parametrize(
    "name,expected_valid,expected_reason",
    [
        ("ubuntu:18.04", True, None),
        ("ubuntu:20.04", True, None),
        (
            "ubuntu:19.04",
            False,
            "Base 'ubuntu:19.04' is not supported (must be 'ubuntu:18.04' or 'ubuntu:20.04')",
        ),
    ],
)
def test_is_base_available(
    provider_class,
    name,
    expected_valid,
    expected_reason,
):
    provider = provider_class()

    valid, reason = provider.is_base_available(name)

    assert (valid, reason) == (expected_valid, expected_reason)
