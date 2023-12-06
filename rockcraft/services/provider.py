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

"""Rockcraft Provider service."""

from craft_application import ProviderService
from overrides import override


class RockcraftProviderService(ProviderService):
    """ProviderService specialization to configure the APT packages."""

    @override
    def setup(self) -> None:
        """Configure the APT packages to be installed in the provider instance."""
        super().setup()
        self.packages.extend(["gpg", "dirmngr"])
