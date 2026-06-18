# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2024 Canonical Ltd.
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

"""Common functionality for Python-based plugins.

This functionality extends Craft-parts' vanilla Python plugin to properly
set the Python interpreter according to the rock's base. Specifically:

- If the base is ubuntu, the venv-created symlinks in bin/ are removed
altogether. This is because of the usrmerge; when the layer is added on
top of the base ubuntu layer bin/ becomes a symlink to usr/bin/, so there
already is a usable Python binary in bin/.
- Since no base (bare or any ubuntu) provides Python by default, the base
interpreter must always be provided by one of the parts. The easiest way
to accomplish this is to add "python3-venv" as a stage-package.
- The shebang in console scripts is hardcoded to "#!/bin/python3". In fact,
every use of Python in the resulting image should be via /bin/python3.
"""

from textwrap import dedent

import craft_parts
from craft_parts.plugins.plugins import PluginType
from craft_parts.plugins.python_v2.python_plugin import PythonPlugin as PythonPluginV2

from .poetry_plugin import PoetryPlugin as PoetryPluginV1
from .python_plugin import PythonPlugin as PythonPluginV1
from .uv_plugin import UvPlugin as UvPluginV1

# Template for the sitecustomize module that we'll add to the payload so that
# the pip-installed packages are found regardless of how the interpreter is
# called.
SITECUSTOMIZE_TEMPLATE = dedent(
    """
    # sitecustomize added by Rockcraft.
    import site
    import sys

    major, minor = sys.version_info.major, sys.version_info.minor
    site_dir = f"/lib/python{major}.{minor}/site-packages"
    dist_dir = "/usr/lib/python3/dist-packages"

    # Add the directory that contains the venv-installed packages.
    site.addsitedir(site_dir)

    if dist_dir in sys.path:
        # Make sure that this site-packages dir comes *before* the base-provided
        # dist-packages dir in sys.path.
        path = sys.path
        site_index = path.index(site_dir)
        dist_index = path.index(dist_dir)

        if dist_index < site_index:
            path[dist_index], path[site_index] = path[site_index], path[dist_index]

    EOF
    """
).strip()


def should_remove_symlinks(info: craft_parts.PartInfo) -> bool:
    """Whether a given Python build should remove the python* venv symlinks.

    :param info: the info for the Python-based part.
    """
    return bool(info.base != "bare")


def get_script_interpreter() -> str:
    """Python is always available in /bin."""
    return "#!/bin/${PARTS_PYTHON_INTERPRETER}"


def wrap_build_commands(parts_commands: list[str]) -> list[str]:
    """Wrap the craft-parts build-commands with Rockraft specific code."""
    commands: list[str] = []

    # Detect whether PARTS_PYTHON_INTERPRETER is a full path (not supported)
    commands.append(
        dedent(
            """
            # Detect whether PARTS_PYTHON_INTERPRETER is an absolute path
            if [[ "${PARTS_PYTHON_INTERPRETER}" = /* ]]; then
                echo "Absolute paths in \"PARTS_PYTHON_INTERPRETER\" are not allowed: ${PARTS_PYTHON_INTERPRETER}"
                exit 1
            fi
            """
        )
    )

    commands.extend(parts_commands)

    # Add a "sitecustomize.py" module to handle the very common case of the
    # rock's interpreter being called as "python3"; in this case, because of
    # the default $PATH, "/usr/bin/python3" ends up being called and that is
    # *not* the venv-aware executable. This sitecustomize adds the location
    # of the pip-installed packages.
    commands.append(
        dedent(
            """
            # Add a sitecustomize.py to import our venv-generated location
            py_version=$(basename $payload_python)
            py_dir=${CRAFT_PART_INSTALL}/usr/lib/${py_version}/
            mkdir -p ${py_dir}
            cat << EOF > ${py_dir}/sitecustomize.py
            """
        )
    )
    commands.append(SITECUSTOMIZE_TEMPLATE)

    # Remove the pyvenv.cfg file that "marks" the virtual environment, because
    # it's not necessary in the presence of the sitecustomize module and this
    # way we get consistent behavior no matter how the interpreter is called.
    commands.append(
        dedent(
            """
            # Remove pyvenv.cfg file in favor of sitecustomize.py
            rm ${CRAFT_PART_INSTALL}/pyvenv.cfg
            """
        )
    )

    return commands


def get_python_plugins(base: str | None) -> dict[str, PluginType]:
    """Get a dict of all supported Python-based plugins.

    :param base: The project's base, if available. This should be the build base.
      If `None`, the function will behave as if the base were the latest LTS.
    """
    plugins: dict[str, PluginType] = {
        "python": PythonPluginV2,
    }

    # For now we'll consider the lack of base (e.g. when running a command without a
    # project) as matching the behavior of the latest LTS, which in this case is Noble.
    if base is None:
        base = "ubuntu@24.04"

    v1_bases = ("ubuntu@20.04", "ubuntu@22.04", "ubuntu@24.04")

    if base in v1_bases:
        plugins["python"] = PythonPluginV1
        plugins["poetry"] = PoetryPluginV1
        plugins["uv"] = UvPluginV1

    return plugins
