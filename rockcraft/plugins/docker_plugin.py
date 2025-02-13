# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2025 Canonical Ltd.
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The Docker plugin."""

import logging
import shlex
from typing import Literal, cast

from craft_parts.plugins import Plugin, PluginProperties, validator
from overrides import override

logger = logging.getLogger(__name__)


class DockerPluginProperties(PluginProperties, frozen=True):
    """The part properties used by the Docker plugin."""

    plugin: Literal["docker"] = "docker"

    meson_parameters: list[str] = []

    # part properties required by the plugin
    source: str  # pyright: ignore[reportGeneralTypeIssues]


class DockerPluginEnvironmentValidator(validator.PluginEnvironmentValidator):
    """Check the execution environment for the Docker plugin.

    :param part_name: The part whose bssh -o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile=/dev/null' -f 'ubuntu@10.102.148.175' -L 8888:10.152.183.248:80 -L 8889:10.152.183.61:5000 -Nuild environment is being validated.
    :param env: A string containing the build step environment setup.
    """

    @override
    def validate_environment(
        self, *, part_dependencies: list[str] | None = None
    ) -> None:
        """Ensure the environment contains dependencies needed by the plugin.

        :param part_dependencies: A list of the parts this part depends on.

        :raises PluginEnvironmentValidationError: If the environment is invalid.
        """
        for dependency in ["docker", "skopeo"]:
            self.validate_dependency(
                dependency=dependency,
                plugin_name="docker",
                part_dependencies=part_dependencies,
            )


class DockerPlugin(Plugin):
    """A plugin for Docker projects.

    The docker plugin requires docker.io, docker-buildx, docker-compose-v2 and skopeo installed
    on your system. This can be achieved by adding the appropriate packages to
    ``build-packages``.

    The docker plugin uses the common plugin keywords as well as those for "sources".
    Additionally, the following plugin-specific keywords can be used:

    - ``docker-parameters``
      (list of strings)
      List of parameters used to configure the docker based project.
    """

    properties_class = DockerPluginProperties
    validator_class = DockerPluginEnvironmentValidator

    @classmethod
    @override
    def get_out_of_source_build(cls) -> bool:
        """Return whether the plugin performs out-of-source-tree builds."""
        return True

    @override
    def get_build_snaps(self) -> set[str]:
        """Return a set of required snaps to install in the build environment."""
        return {"docker", "jq"}

    @override
    def get_build_packages(self) -> set[str]:
        """Return a set of required packages to install in the build environment."""
        return {"skopeo"}

    @override
    def get_build_environment(self) -> dict[str, str]:
        """Return a dictionary with the environment to use in the build step."""
        return {}

    @override
    def get_build_commands(self) -> list[str]:
        """Return a list of commands to run during the build step."""
        options = cast(DockerPluginProperties, self._options)

        docker_cmd = [
            "docker",
            "build",
            "-t",
            f"{self._part_info.part_name}:1",
            str(self._part_info.part_src_subdir),
        ]
        if options.meson_parameters:
            docker_cmd.extend(shlex.quote(p) for p in options.meson_parameters)

        skopeo_cmd = [
            "skopeo",
            "copy",
            f"docker-daemon:{self._part_info.part_name}:1",
            f"dir:{self._part_info.part_install_dir}",
        ]

        tar_cmd = [
            f"cd {self._part_info.part_install_dir};",
            "cat",
            f"{self._part_info.part_install_dir}/manifest.json",
            "|",
            "jq '.layers[].digest | split(\":\") | nth(1)'",
            "|",
            'while IFS= read -r line; do line=${line%\\"}; line=${line#\\"}; [[ -n "$line" ]] && tar xvf $line --directory '
            f"{self._part_info.part_install_dir}; done;",
            "rm ????????????????????????????????????????????????????????????????;",
            "rm manifest.json;",
            "rm version;",
        ]

        return [
            f"DESTDIR={self._part_info.part_install_dir} ",
            " ".join(docker_cmd),
            " ".join(skopeo_cmd),
            " ".join(tar_cmd),
        ]
