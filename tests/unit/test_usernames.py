# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2023 Canonical Ltd
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

import pydantic
import pytest

from rockcraft import usernames


def test_type(check):
    check.is_instance(usernames.SUPPORTED_GLOBAL_USERNAMES, dict)


def test_not_empty(check):
    check.greater(len(usernames.SUPPORTED_GLOBAL_USERNAMES), 0)


def test_structure(check):
    check.is_instance(
        usernames.GlobalUser(username="confined_foo", uid=584795).get_dict(), dict
    )
    for user, info in usernames.SUPPORTED_GLOBAL_USERNAMES.items():
        check.is_instance(user, str)
        check.is_instance(info, dict)
        check.is_in("uid", info)
        check.is_instance(info["uid"], int)


def test_bad_prefix():
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        usernames.GlobalUser(username="badprefix_foo", uid=584795)


def test_bad_uid():
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        usernames.GlobalUser(username="confined_foo", uid=5)

    with pytest.raises(pydantic.error_wrappers.ValidationError):
        usernames.GlobalUser(username="confined_foo", uid=58479500)
