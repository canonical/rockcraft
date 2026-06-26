import importlib
import datetime
import os
import pathlib
import sys
import textwrap

import craft_parts_docs
import rockcraft

# Configuration for the Sphinx documentation builder.
# All configuration specific to your project should be done in this file.
#
# If you're new to Sphinx and don't want any advanced or custom features,
# just go through the items marked 'TODO'.
#
# A complete list of built-in Sphinx configuration values:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
#
# The Sphinx Stack uses the Canonical Sphinx theme to keep all documentation consistent
# and on brand:
# https://github.com/canonical/canonical-sphinx


#######################
# Project information #
#######################

# Project name
project = "Rockcraft"

# Author name; used in the default copyright statement in the page footer
author = "Canonical Ltd."

# Version string in sidebar
if os.environ.get("READTHEDOCS_VERSION_TYPE", "external") == "external":  # PR or local build
    # Because of setuptools-scm, we can safely assume the version starts with `n.n`
    major, minor, *_ = rockcraft.__version__.split(".")
    release = f"{major}.{minor}"
else:  # Branch build
    rtd_version = os.environ.get("READTHEDOCS_VERSION", "latest")
    release = "dev" if rtd_version == "latest" else rtd_version

# The year in the copyright statement
copyright = f"2022-{datetime.date.today().year}"


# Documentation website URL
ogp_site_url = "https://documentation.ubuntu.com/rockcraft"

#Preview name of the documentation website
ogp_site_name = project

#Preview image URL
ogp_image = "https://assets.ubuntu.com/v1/253da317-image-document-ubuntudocs.svg"

# Product favicon; shown in bookmarks, browser tabs, etc.
# html_favicon = '.sphinx/_static/favicon.png'

# Dictionary of values to pass into the Sphinx context for all pages:
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_context
html_context = {
    "product_page": "ubuntu.com/containers",
    # Product tag image; the orange part of your logo, shown in the page header
    # "product_tag": "_static/tag.png",
    # Your Discourse instance URL
    "discourse": "https://discourse.ubuntu.com/c/rocks/117",
    # Your Matrix channel URL
    "matrix": "https://matrix.to/#/#rockcraft:ubuntu.com",
    # Your documentation GitHub repository URL. If set, links for viewing the
    # documentation source files and creating GitHub issues are added at the bottom of
    # each page.
    "github_url": "https://github.com/canonical/rockcraft",
    # Docs branch in the repo; used in links for viewing the source files
    "repo_default_branch": "main",
    # Docs location in the repo; used in links for viewing the source files
    "repo_folder": "/docs/",
    # List contributors on individual pages
    "display_contributors": False,
    # Required for feedback button
    "github_issues": 'enabled',
    # Passes the top-level 'author' value to the theme
    "author": author,
    # Documentation license information
    "license": {
        "name": "GPL-3.0",
        "url": "https://github.com/canonical/rockcraft/blob/main/LICENSE",
    },
}

# Enable the edit button on pages
html_theme_options = {
    "source_edit_link": "https://github.com/canonical/rockcraft",
}

# slug = ''


#######################
# Sitemap configuration: https://sphinx-sitemap.readthedocs.io/
#######################

# Use RTD canonical URL to ensure duplicate pages have a specific canonical URL
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "/")

# sphinx-sitemap uses html_baseurl to generate the full URL for each page:
sitemap_url_scheme = '{link}'

# Include `lastmod` dates in the sitemap:
# sitemap_show_lastmod = True

# Pages excluded from the sitemap:
sitemap_excludes = [
    '404/',
    'genindex/',
    'search/',
]


#######################
# Template and asset locations
#######################

html_static_path = ["_static"]
templates_path = ["_templates"]

#############
# Redirects #
#############

# Add redirects to the 'redirects.txt' file
# https://sphinxext-rediraffe.readthedocs.io/en/latest/

# To set up redirects in the Read the Docs project dashboard:
# https://docs.readthedocs.io/en/stable/guides/redirects.html

rediraffe_redirects = "redirects.txt"

# Strips '/index.html' from destination URLs when building with 'dirhtml'
rediraffe_dir_only = True

############################
# sphinx-llm configuration #
############################

# This description is included in llms.txt to provide some initial context for your
# product docs.
llms_txt_description = textwrap.dedent(
    """\
    This is the documentation for Rockcraft, the tool for assembling rocks. Rocks are
    OCI-compliant images with extra security features and a smaller storage footprint.
    """
)

# The base URL for references built by sphinx-markdown-builder.
if os.environ.get("READTHEDOCS"):
    markdown_http_base = html_baseurl

###########################
# Link checker exceptions #
###########################

# Whole sites and individuals URLs to ignore
linkcheck_ignore = [
    # Entire domains to ignore due to flakiness or issues
    r"^https://github.com",
    r"^https://www.gnu.org/",
    r"^https://crates.io/",
    r"^https://([\w-]*\.)?npmjs.org",
    r"^https://rsync.samba.org",
    r"^https://ubuntu.com",
    r"^https://www.freedesktop.org/",
    r"^https://www.npmjs.com/",
    r"^https://github.com/canonical/[a-z]*craft[a-z-]*/releases/.*",
    r"^https://matrix.to/#",
    "https://github.com/canonical/craft-actions#rockcraft-pack",
    "https://github.com/canonical/spread#selecting-which-tasks-to-run",
    "https://matrix.to/#/#rocks:ubuntu.com",
    "https://matrix.to/#/#rockcraft:ubuntu.com",
    "https://matrix.to/#/#12-factor-charms:ubuntu.com",
    "https://specs.opencontainers.org/image-spec/config/",
    "https://specs.opencontainers.org/image-spec/annotations/",
    "https://canonical.com/#get-in-touch#",
    "http://127.0.0.1:8000/",
    # 2026-06-03: Ignore Canonical sites until filtering is resolved
    "https://snapcraft.io",
    "https://juju.is",
]

# Anchor strings to ignore
# linkcheck_anchors_ignore = []
# Don't check links in the "common" subdirectory, as those are the responsibility of
# the libraries.
linkcheck_exclude_documents = ["^common/.*"]

# give linkcheck multiple tries on failure
linkcheck_retries = 20

linkcheck_report_timeouts_as_broken = False

########################
# Configuration extras #
########################

# Custom Sphinx extensions; see
# https://www.sphinx-doc.org/en/master/usage/extensions/index.html

extensions = [
    "canonical_sphinx",
    "notfound.extension",
    "sphinx_design",
    "sphinx_rerediraffe",
    # "sphinx_tabs.tabs",
    # "sphinxcontrib.jquery",
    "sphinxext.opengraph",
    # "sphinx_config_options",
    # "sphinx_contributor_listing",
    # "sphinx_filtered_toctree",
    "sphinx_llm.txt",
    "sphinx_related_links",
    "sphinx_roles",
    "sphinx_terminal",
    "sphinx_copybutton",
    # "sphinx_ubuntu_images",
    # "sphinx_youtube_links",
    # "sphinxcontrib.cairosvgconverter",
    # "sphinx_last_updated_by_git",
    "sphinx.ext.intersphinx",
    "sphinx_sitemap",
    # Custom Craft extensions
    "pydantic_kitbash",
    #"sphinx-pydantic",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",  # must be loaded after napoleon
    "sphinxcontrib.details.directive",
    "sphinx_toolbox.collapse",
    # "sphinx_substitution_extensions",
    ]

# Excludes files or directories from processing

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    # Excluded here because they are either included explicitly in other
    # documents (so they generate "duplicate label" errors) or they aren't
    # used in this documentation at all (so they generate "unreferenced"
    # errors).
    "common/craft-parts/explanation/file-migration.rst",
    "common/craft-parts/explanation/overlay_parameters.rst",
    "common/craft-parts/explanation/overlays.rst",
    "common/craft-parts/explanation/how_parts_are_built.rst",
    "common/craft-parts/explanation/overlay_step.rst",
    "common/craft-parts/explanation/gradle_plugin.rst",
    "common/craft-parts/how-to/customise-the-build-with-craftctl.rst",
    "common/craft-parts/how-to/use_parts.rst",
    "common/craft-parts/how-to/include_files.rst",
    "common/craft-parts/reference/partition_specific_output_directory_variables.rst",
    "common/craft-parts/reference/parts_steps.rst",
    "common/craft-parts/reference/step_execution_environment.rst",
    "common/craft-parts/reference/step_output_directories.rst",
    "common/craft-parts/reference/part_properties.rst",
    "common/craft-parts/reference/plugins/colcon_plugin.rst",
    "common/craft-parts/reference/plugins/dotnet_plugin.rst",
    "common/craft-parts/reference/plugins/dotnet_v2_plugin.rst",
    "common/craft-parts/reference/plugins/poetry_plugin.rst",
    "common/craft-parts/reference/plugins/python_plugin.rst",
    "common/craft-parts/reference/plugins/python_v2_plugin.rst",
    "common/craft-parts/reference/plugins/uv_plugin.rst",
    "common/craft-parts/reference/plugins/ruby_plugin.rst",
    "common/craft-application/how-to-guides/build-remotely.rst",
    "common/craft-application/how-to-guides/reuse-packages-between-builds.rst",
    "common/craft-application/reference/fetch-service.rst",
    "common/craft-application/reference/remote-builds.rst",
    "common/craft-application/reference/strict-platform-names.rst",
    # Extra non-craft-parts exclusions can be added after this comment
    "reuse/*",
    "README.md",
]

# Adds custom CSS files, located remotely or in 'html_static_path'.
html_css_files = ["https://assets.ubuntu.com/v1/d86746ef-cookie_banner.css"]

# Adds custom JavaScript files, located remotely or in 'html_static_path'.
html_js_files = ["https://assets.ubuntu.com/v1/287a5e8f-bundle.js"]

# Appends extra markup to the end of every document written in reST
rst_epilog = """
.. include:: /reuse/links.txt
"""

# Feedback button at the top; enabled by default
# disable_feedback_button = True

# Your manpage URL
# manpages_url = 'https://manpages.ubuntu.com/manpages/{codename}/en/' + \
#     'man{section}/{page}.{section}.html'

# Specifies a reST snippet to be prepended to each .rst file
# This defines a :center: role that centers table cell content.
# This defines a :h2: role that styles content for use with PDF generation.
rst_prolog = """
.. role:: center
   :class: align-center
.. role:: h2
    :class: hclass2
.. role:: woke-ignore
    :class: woke-ignore
.. role:: vale-ignore
    :class: vale-ignore
"""

# Add configuration for intersphinx mapping
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "12-factor": ("https://canonical.com/juju/docs/12-factor/latest", None),
    "charmcraft": ("https://documentation.ubuntu.com/charmcraft/stable", None),
    "pebble": ("https://ubuntu.com/docs/pebble/", None),
    "chisel": ("https://ubuntu.com/chisel/docs/latest/", None),
}
# See also:
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#confval-intersphinx_disabled_reftypes
intersphinx_disabled_reftypes = ["*"]


##############################
# Custom Craft configuration #
##############################

# Type hints configuration
set_type_checking_flag = True
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True

# Automated documentation
project_dir = pathlib.Path(__file__).parents[1].resolve()
sys.path.insert(0, str(project_dir.absolute()))

def generate_cli_docs(nil):
    gen_cli_docs_path = (project_dir / "tools/docs/gen_cli_docs.py").resolve()
    os.system("%s %s" % (gen_cli_docs_path, project_dir / "docs"))


def setup(app):
    app.connect("builder-inited", generate_cli_docs)

# Setup libraries documentation snippets for use in rockcraft docs.
common_docs_path = pathlib.Path(__file__).parent / "common"
def link_common_docs(library_name: str) -> None:
    """Create a link to the appropriate common documentation directory."""
    common_lib_path = common_docs_path / library_name

    docs_module_name = f"{library_name.replace('-', '_')}_docs"
    docs_module = importlib.import_module(docs_module_name)
    docs_path = pathlib.Path(docs_module.__file__).parent / library_name  # pyright: ignore[reportArgumentType]

    if common_lib_path.is_symlink() and common_lib_path.readlink() == docs_path:
        return

    common_lib_path.unlink(missing_ok=True)
    common_lib_path.symlink_to(docs_path, target_is_directory=True)

link_common_docs("craft-parts")
link_common_docs("craft-application")

# Do (not) include module names.
add_module_names = True

# Enable support for google-style instance attributes.
napoleon_use_ivar = True

# For documentation on documentation.ubuntu.com, we also must add the slug.
url_version = ""
url_lang = ""
slug = "rockcraft"

# Determine if the URL uses versions and language
if (
    "READTHEDOCS_CANONICAL_URL" in os.environ
    and os.environ["READTHEDOCS_CANONICAL_URL"]
):
    url_parts = os.environ["READTHEDOCS_CANONICAL_URL"].split("/")

    if (
        len(url_parts) >= 2
        and "READTHEDOCS_VERSION" in os.environ
        and os.environ["READTHEDOCS_VERSION"] == url_parts[-2]
    ):
        url_version = url_parts[-2] + "/"

    if (
        len(url_parts) >= 3
        and "READTHEDOCS_LANGUAGE" in os.environ
        and os.environ["READTHEDOCS_LANGUAGE"] == url_parts[-3]
    ):
        url_lang = url_parts[-3] + "/"

# Set notfound_urls_prefix to the slug (if defined) and the version/language affix
if slug:
    notfound_urls_prefix = "/" + slug + "/" + url_lang + url_version
elif len(url_lang + url_version) > 0:
    notfound_urls_prefix = "/" + url_lang + url_version
else:
    notfound_urls_prefix = ""

notfound_context = {
    "title": "Page not found",
    "body": "<p><strong>Sorry, but the documentation page that you are looking for was not found.</strong></p>\n\n<p>Documentation changes over time, and pages are moved around. We try to redirect you to the updated content where possible, but unfortunately, that didn't work this time (maybe because the content you were looking for does not exist in this version of the documentation).</p>\n<p>You can try to use the navigation to locate the content you're looking for, or search for a similar page.</p>\n",
}
