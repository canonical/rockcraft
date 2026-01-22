# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2026 Canonical Ltd.
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

"""Base-specific plugin groups for Rockcraft."""

from craft_parts.plugins.ant_plugin import AntPlugin
from craft_parts.plugins.autotools_plugin import AutotoolsPlugin
from craft_parts.plugins.base import Plugin
from craft_parts.plugins.cargo_use_plugin import CargoUsePlugin
from craft_parts.plugins.cmake_plugin import CMakePlugin
from craft_parts.plugins.dotnet_plugin import DotnetPlugin
from craft_parts.plugins.dump_plugin import DumpPlugin
from craft_parts.plugins.go_plugin import GoPlugin
from craft_parts.plugins.go_use_plugin import GoUsePlugin
from craft_parts.plugins.gradle_plugin import GradlePlugin
from craft_parts.plugins.jlink_plugin import JLinkPlugin
from craft_parts.plugins.make_plugin import MakePlugin
from craft_parts.plugins.maven_plugin import MavenPlugin
from craft_parts.plugins.maven_use_plugin import MavenUsePlugin
from craft_parts.plugins.meson_plugin import MesonPlugin
from craft_parts.plugins.nil_plugin import NilPlugin
from craft_parts.plugins.npm_plugin import NpmPlugin
from craft_parts.plugins.qmake_plugin import QmakePlugin
from craft_parts.plugins.rust_plugin import RustPlugin
from craft_parts.plugins.scons_plugin import SConsPlugin

from .register import get_plugins as get_rockcraft_plugins


def get_plugin_group(
    build_base: str,
) -> dict[str, type[Plugin]]:
    """Get the full set of plugins for a given base."""
    # Since this comes from a BuildInfo, the devel base might be referred to as ubuntu@devel
    if build_base == "ubuntu@devel":
        build_base = "devel"
    # Baseline Craft Parts plugins that work on the base
    group = _PLUGINS[build_base]
    # Rockcraft-specific overrides/additions
    group |= get_rockcraft_plugins(build_base)
    return group


# Minimal set of plugins that are expected to work on all supported bases.
# Note the absence of Python plugins - we add rockcraft-specific ones per-base.
_ROCKCRAFT_DEFAULT: dict[str, type[Plugin]] = {
    "ant": AntPlugin,
    "autotools": AutotoolsPlugin,
    "cargo-use": CargoUsePlugin,
    "cmake": CMakePlugin,
    "dump": DumpPlugin,
    "go": GoPlugin,
    "go-use": GoUsePlugin,
    "gradle": GradlePlugin,
    "jlink": JLinkPlugin,
    "make": MakePlugin,
    "maven": MavenPlugin,
    "maven-use": MavenUsePlugin,
    "meson": MesonPlugin,
    "nil": NilPlugin,
    "npm": NpmPlugin,
    "qmake": QmakePlugin,
    "rust": RustPlugin,
    "scons": SConsPlugin,
}

# Dotnet gets separated because we need to look into supporting the v2 of the plugin.
_DOTNET_V1: dict[str, type[Plugin]] = {
    "dotnet": DotnetPlugin,
}

_LEGACY_PLUGINS: dict[str, type[Plugin]] = _ROCKCRAFT_DEFAULT | _DOTNET_V1

_PLUGINS: dict[str, dict[str, type[Plugin]]] = {
    "ubuntu@20.04": _LEGACY_PLUGINS,
    "ubuntu@22.04": _LEGACY_PLUGINS,
    "ubuntu@24.04": _LEGACY_PLUGINS,
    "ubuntu@25.10": _ROCKCRAFT_DEFAULT,
    "devel": _ROCKCRAFT_DEFAULT,
}
