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

"""List of allowed global usernames/UIDs (analogously to SnapD)."""

import pydantic


class GlobalUser(pydantic.BaseModel):
    """User object with the allowed attributes."""

    username: str
    uid: int = pydantic.Field(gt=584791, le=585287)

    @pydantic.validator("username", always=True)
    @classmethod
    def _validate_license(cls, username: str) -> str:
        """Make sure the provided username has the right prefix."""
        prefix = "confined_"
        err = f"All global usernames must start with the prefix {prefix}."
        assert username.startswith(prefix), err

        return username

    def get_dict(self) -> dict:
        """Cast the object into a dict using the username as the key."""
        return {self.username: {"uid": self.uid}}


SUPPORTED_GLOBAL_USERNAMES = {
    **GlobalUser(username="confined_daemon", uid=584792).get_dict(),
}
