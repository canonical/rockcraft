import datetime
import os
import pathlib
import sys

import craft_parts_docs
import rockcraft

# Configuration for the Sphinx documentation builder.
# All configuration specific to your project should be done in this file.
#
# A complete list of built-in Sphinx configuration values:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
#
# Our starter pack uses the custom Canonical Sphinx extension
# to keep all documentation based on it consistent and on brand:
# https://github.com/canonical/canonical-sphinx


#######################
# Project information #
#######################

# Project name
project = "Rockcraft"
author = "Canonical Ltd."

# Sidebar documentation title; best kept reasonably short
# The full version, including alpha/beta/rc tags
release = rockcraft.__version__
# The commit hash in the dev release version confuses the spellchecker
if ".post" in release:
    release = "dev"

html_title = project + " documentation"

# Copyright string; shown at the bottom of the page
copyright = "2022-%s, %s" % (datetime.date.today().year, author)

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
    "product_page": "",  # Rockcraft doesn't have a marketing page
    "matrix": "https://matrix.to/#/#rockcraft:ubuntu.com",
    "discourse": "https://discourse.ubuntu.com/c/rocks/117",
    "github_url": "https://github.com/canonical/rockcraft",
    "repo_default_branch": "main",
    "repo_folder": "/docs/",
    "display_contributors": False,
    "github_issues": 'enabled',
}

#html_extra_path = []

html_theme_options = {
    "source_edit_link": "https://github.com/canonical/rockcraft",
}

# Project slug; see https://meta.discourse.org/t/what-is-category-slug/87897
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

# Exclude generated pages from the sitemap:
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

rediraffe_redirects = "redirects.txt"


###########################
# Link checker exceptions #
###########################

# A regex list of URLs that are ignored by 'make linkcheck'
linkcheck_anchors_ignore = [
    "#",
    ":",
    r"https://github\.com/.*",
    "slide definitions",
]
linkcheck_ignore = [
    # GitHub aggressively rate limits us
    r"^https://github.com/",
    # Entire domains to ignore due to flakiness or issues
    r"^https://www.gnu.org/",
    r"^https://crates.io/",
    r"^https://([\w-]*\.)?npmjs.org",
    r"^https://rsync.samba.org",
    r"^https://ubuntu.com",
    r"^https://www.freedesktop.org/",
    r"^https://www.npmjs.com/",
    r"^https://github.com/canonical/[a-z]*craft[a-z-]*/releases/.*",
    "https://matrix.to/#",
    "https://github.com/canonical/craft-actions#rockcraft-pack",
    "https://github.com/canonical/spread#selecting-which-tasks-to-run",
    "https://juju.is/cloud-native-kubernetes-usage-report-2021#selection-criteria-for-container-images",
    "https://matrix.to/#/#rocks:ubuntu.com",
    "https://matrix.to/#/#rockcraft:ubuntu.com",
    "https://matrix.to/#/#12-factor-charms:ubuntu.com",
    "https://specs.opencontainers.org/image-spec/config/",
]

# Don't check links in the "common" subdirectory, as those are the responsibility of
# the libraries.
linkcheck_exclude_documents = ["^common/.*"]

# give linkcheck multiple tries on failure
linkcheck_retries = 20

########################
# Configuration extras #
########################

# Custom Sphinx extensions; see
# https://www.sphinx-doc.org/en/master/usage/extensions/index.html

extensions = [
    "canonical_sphinx",
    "notfound.extension",
    # "sphinx_design",
    # "sphinx_tabs.tabs",
    # "sphinxcontrib.jquery",
    # "sphinxext.opengraph",
    # "sphinx_config_options",
    # "sphinx_contributor_listing",
    # "sphinx_filtered_toctree",
    # "sphinx_related_links",
    "sphinx_roles",
    "sphinx_terminal",
    # "sphinx_ubuntu_images",
    # "sphinx_youtube_links",
    # "sphinxcontrib.cairosvgconverter",
    # "sphinx_last_updated_by_git",
    # "sphinx.ext.intersphinx",
    "sphinx_sitemap",
    # Custom Craft extensions
    "pydantic_kitbash",
    # "sphinx-pydantic",
    "sphinxext.rediraffe",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",  # must be loaded after napoleon
    "sphinxcontrib.details.directive",
    "sphinx_toolbox.collapse",
    "sphinx.ext.intersphinx",
    # "sphinx_substitution_extensions",
    ]

# Excludes files or directories from processing

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "env",
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
    "common/craft-parts/reference/partition_specific_output_directory_variables.rst",
    "common/craft-parts/reference/parts_steps.rst",
    "common/craft-parts/reference/step_execution_environment.rst",
    "common/craft-parts/reference/step_output_directories.rst",
    "common/craft-parts/reference/part_properties.rst",
    "common/craft-parts/reference/plugins/colcon_plugin.rst",
    "common/craft-parts/reference/plugins/poetry_plugin.rst",
    "common/craft-parts/reference/plugins/python_plugin.rst",
    "common/craft-parts/reference/plugins/python_v2_plugin.rst",
    "common/craft-parts/reference/plugins/uv_plugin.rst",
    "common/craft-parts/reference/plugins/ruby_plugin.rst",
    # Extra non-craft-parts exclusions can be added after this comment
    "reuse/*",
    "README.md",
]

# Adds custom CSS files, located under 'html_static_path'
html_css_files = ["css/cookie-banner.css"]

# Adds custom JavaScript files, located under 'html_static_path'
html_js_files = [
    "js/bundle.js",
]

# Specifies a reST snippet to be appended to each .rst file
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

# Workaround for https://github.com/canonical/canonical-sphinx/issues/34
if "discourse_prefix" not in html_context and "discourse" in html_context:
    html_context["discourse_prefix"] = f"{html_context['discourse']}/t/"

# Add configuration for intersphinx mapping
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "12-factor": (
        "https://canonical-12-factor-app-support.readthedocs-hosted.com/latest/",
        None,
    ),
    "charmcraft": ("https://documentation.ubuntu.com/charmcraft/stable/", None),
    "pebble": ("https://documentation.ubuntu.com/pebble", None),
    "chisel": ("https://documentation.ubuntu.com/chisel/en/latest", None),
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

# Setup libraries documentation snippets for use in rockcraft docs.
common_docs_path = pathlib.Path(__file__).parent / "common"
craft_parts_docs_path = pathlib.Path(craft_parts_docs.__file__).parent / "craft-parts"
(common_docs_path / "craft-parts").unlink(missing_ok=True)
(common_docs_path / "craft-parts").symlink_to(
    craft_parts_docs_path, target_is_directory=True
)

# Do (not) include module names.
add_module_names = True

# Enable support for google-style instance attributes.
napoleon_use_ivar = True

# TODO: this is a boilerplate copy from the sphinx-docs. It should
# be built on top of it instead of duplicating its content
# Not found
# The URL prefix for the notfound extension depends on whether the documentation uses versions.
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

# region Autgenerate documentation

def generate_cli_docs(nil):
    gen_cli_docs_path = (project_dir / "tools/docs/gen_cli_docs.py").resolve()
    os.system("%s %s" % (gen_cli_docs_path, project_dir / "docs"))


def setup(app):
    app.connect("builder-inited", generate_cli_docs)

# endregion

# We have many links on sites that frequently respond with 503s to GitHub runners.
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-linkcheck_retries
linkcheck_retries = 20
linkcheck_anchors_ignore = ["#", ":", "slice-definitions"]
linkcheck_ignore = [
    # Ignore releases, since we'll include the next release before it exists.
    r"^https://github.com/canonical/[a-z]*craft[a-z-]*/releases/.*",
    # Entire domains to ignore due to flakiness or issues
    r"^https://www.gnu.org/",
    r"^https://crates.io/",
    r"^https://([\w-]*\.)?npmjs.org",
    r"^https://rsync.samba.org",
    r"^https://ubuntu.com",
    "https://github.com/canonical/craft-actions#rockcraft-pack",
    "https://github.com/canonical/spread#selecting-which-tasks-to-run",
    "https://juju.is/cloud-native-kubernetes-usage-report-2021#selection-criteria-for-container-images",
    "https://matrix.to/#/#rocks:ubuntu.com",
    "https://matrix.to/#/#rockcraft:ubuntu.com",
    "https://matrix.to/#/#12-factor-charms:ubuntu.com",
    "https://specs.opencontainers.org/image-spec/config/",
    "https://canonical.com/#get-in-touch#",
]
# Don't check links in the "common" subdirectory, as those are the responsibility of
# the libraries.
linkcheck_exclude_documents = ["^common/.*"]
