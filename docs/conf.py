# Copyright 2023-2024 Canonical Ltd.
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

import datetime
import os
import pathlib
import sys

import craft_parts_docs

project_dir = pathlib.Path("..").resolve()
sys.path.insert(0, str(project_dir.absolute()))

import rockcraft  # noqa: E402

project = "Rockcraft"
author = "Canonical Group Ltd"

copyright = "2022-%s, %s" % (datetime.date.today().year, author)

# The full version, including alpha/beta/rc tags
release = rockcraft.__version__
if ".post" in release:
    # The commit hash in the dev release version confuses the spellchecker
    release = "dev"

# region Configuration for canonical-sphinx
ogp_site_url = "https://canonical-rockcraft.readthedocs-hosted.com/"
ogp_site_name = project

html_context = {
    "product_page": "github.com/canonical/rockcraft",
    "discourse": "https://discourse.ubuntu.com/c/rocks/117",
    "github_url": "https://github.com/canonical/rockcraft",
}

extensions = [
    "canonical_sphinx",
]
# endregion

extensions.extend(
    [
        "sphinx.ext.autodoc",
        "sphinx.ext.ifconfig",
        "sphinx.ext.napoleon",
        "sphinx.ext.viewcode",
        "sphinx_autodoc_typehints",  # must be loaded after napoleon
        "sphinxcontrib.details.directive",
        "sphinx_toolbox.collapse",
    ]
)

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "env",
    "sphinx-starter-pack",
    # Excluded here because they are either included explicitly in other
    # documents (so they generate "duplicate label" errors) or they aren't
    # used in this documentation at all (so they generate "unreferenced"
    # errors).
    "common/craft-parts/explanation/filesets.rst",
    "common/craft-parts/explanation/lifecycle.rst",
    "common/craft-parts/explanation/overlay_parameters.rst",
    "common/craft-parts/explanation/overlays.rst",
    "common/craft-parts/explanation/parts.rst",
    "common/craft-parts/explanation/how_parts_are_built.rst",
    "common/craft-parts/explanation/overlay_step.rst",
    "common/craft-parts/how-to/craftctl.rst",
    "common/craft-parts/reference/parts_steps.rst",
    "common/craft-parts/reference/step_execution_environment.rst",
    "common/craft-parts/reference/step_output_directories.rst",
    "common/craft-parts/reference/plugins/python_plugin.rst",
    # Extra non-craft-parts exclusions can be added after this comment
]

linkcheck_ignore = [
    "http://0.0.0.0:8080",
    "https://github.com/canonical/craft-actions#rockcraft-pack",
    "https://github.com/canonical/pebble#layer-specification",
    "https://juju.is/cloud-native-kubernetes-usage-report-2021#selection-criteria-for-container-images",
    "https://matrix.to/#/#rocks:ubuntu.com",
]

rst_epilog = """
.. include:: /reuse/links.txt
"""

# region Options for extensions

# Github config
github_username = "canonical"
github_repository = "rockcraft"

# Do (not) include module names.
add_module_names = True

# sphinx_autodoc_typehints
set_type_checking_flag = True
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True
linkcheck_anchors_ignore = ["slice-definitions"]

# Enable support for google-style instance attributes.
napoleon_use_ivar = True

# endregion


def generate_cli_docs(nil):
    gen_cli_docs_path = (project_dir / "tools" / "docs" / "gen_cli_docs.py").resolve()
    os.system("%s %s" % (gen_cli_docs_path, project_dir / "docs"))


def setup(app):
    app.connect("builder-inited", generate_cli_docs)


# Setup libraries documentation snippets for use in rockcraft docs.
common_docs_path = pathlib.Path(__file__).parent / "common"
craft_parts_docs_path = pathlib.Path(craft_parts_docs.__file__).parent / "craft-parts"
(common_docs_path / "craft-parts").unlink(missing_ok=True)
(common_docs_path / "craft-parts").symlink_to(
    craft_parts_docs_path, target_is_directory=True
)
