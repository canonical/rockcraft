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
import pytest

from rockcraft import errors, extensions
from rockcraft.extensions.extension import Extension


class FakeExtension1(Extension):
    """A fake test Extension"""

    NAME = "fake-extension-1"


class FakeExtension2(Extension):
    """A fake test Extension"""

    NAME = "fake-extension-2"


class FakeExtension3(Extension):
    """A fake test Extension"""

    NAME = "fake-extension-3"


@pytest.fixture
def fake_extensions(mock_extensions):
    for ext_class in (FakeExtension1, FakeExtension2):
        extensions.register(ext_class.NAME, ext_class)


def test_get_extension_names(fake_extensions):
    assert extensions.get_extension_names() == [
        FakeExtension1.NAME,
        FakeExtension2.NAME,
    ]


def test_get_extension_class(fake_extensions):
    assert extensions.get_extension_class(FakeExtension1.NAME) is FakeExtension1
    assert extensions.get_extension_class(FakeExtension2.NAME) is FakeExtension2


def test_get_extension_class_error(fake_extensions):
    with pytest.raises(errors.ExtensionError):
        extensions.get_extension_class(FakeExtension3.NAME)


def test_register(fake_extensions):
    assert FakeExtension3.NAME not in extensions.get_extension_names()
    extensions.register(FakeExtension3.NAME, FakeExtension3)
    assert FakeExtension3.NAME in extensions.get_extension_names()
    assert extensions.get_extension_class(FakeExtension3.NAME) is FakeExtension3


def test_unregister(fake_extensions):
    assert extensions.get_extension_class(FakeExtension1.NAME) is FakeExtension1
    extensions.unregister(FakeExtension1.NAME)
    with pytest.raises(errors.ExtensionError):
        extensions.get_extension_class(FakeExtension1.NAME)
