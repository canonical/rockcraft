"""
check-pythonpath.py: Script that looks for the distro-installed "dist-packages"
dir and the venv-installed "site-packages" dir in "sys.path" and fails if
dist-packages comes _before_ site-packages.
"""

import sys

major, minor = sys.version_info.major, sys.version_info.minor
site_dir = f"/lib/python{major}.{minor}/site-packages"
dist_dir = "/usr/lib/python3/dist-packages"

site_index = sys.path.index(site_dir)
dist_index = sys.path.index(dist_dir)

if dist_index < site_index:
    raise RuntimeError(
        f"dist-packages ({dist_dir} at index {dist_index}) is before "
        f"site-packages ({site_dir} at index {site_index}) in sys.path"
    )
