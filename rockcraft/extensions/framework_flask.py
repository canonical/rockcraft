# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2022 Canonical Ltd.
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

"""Generic GNOME extension to support core22 and onwards."""
import dataclasses
import functools
import re
from typing import Any, Dict, List, Optional, Tuple

from overrides import overrides

from .extension import Extension, get_extensions_data_dir, prepend_to_env


class FrameworkFlask(Extension):
    """An extension that eases the creation of ROCKS that integrate with Flask."""

    @staticmethod
    @overrides
    def get_supported_bases() -> Tuple[str, ...]:
        return ("ubuntu:22.04",)

    @staticmethod
    @overrides
    def is_experimental(base: Optional[str]) -> bool:
        return False

    @overrides
    def get_services_snippet(self) -> Dict[str, Any]:
        return {}

    @overrides
    def get_root_snippet(self) -> Dict[str, Any]:
        return {}

    @overrides
    def get_parts_snippet(self) -> Dict[str, Any]:
        return {}
