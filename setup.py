#!/usr/bin/env python3
#
# Copyright 2021 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#


"""The setup script."""
import os
from typing import List, Tuple

from setuptools import setup


def recursive_data_files(
    directory: str, install_directory: str
) -> List[Tuple[str, List[str]]]:
    """Find all data files in directory, recursively, and add them to install_directory."""
    data_files = []
    for root, _directories, file_names in os.walk(directory):
        file_paths = [os.path.join(root, file_name) for file_name in file_names]
        data_files.append((os.path.join(install_directory, root), file_paths))
    return data_files


setup(data_files=recursive_data_files("extensions", "share/rockcraft"))
