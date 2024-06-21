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

"""Creation of minimalist rockcraft projects."""
import pathlib
import re
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

from craft_application.commands import AppCommand
from craft_cli import emit
from overrides import overrides  # type: ignore[reportUnknownVariableType]

from rockcraft import errors
from rockcraft.models.project import INVALID_NAME_MESSAGE, NAME_REGEX

if TYPE_CHECKING:
    import argparse


def init(rockcraft_yaml_content: str) -> None:
    """Initialize a rockcraft project.

    :param rockcraft_yaml_content: Content of the rockcraft.yaml file
    :raises RockcraftInitError: raises initialization error in case of conflicts
    with existing rockcraft.yaml files
    """
    rockcraft_yaml_path = Path("rockcraft.yaml")

    if rockcraft_yaml_path.is_file():
        raise errors.RockcraftInitError(f"{rockcraft_yaml_path} already exists!")

    if Path(f".{rockcraft_yaml_path.name}").is_file():
        raise errors.RockcraftInitError(f".{rockcraft_yaml_path} already exists!")

    rockcraft_yaml_path.write_text(rockcraft_yaml_content)

    emit.progress(f"Created {rockcraft_yaml_path}.")


class InitCommand(AppCommand):
    """Initialize a rockcraft project."""

    _INIT_TEMPLATES = {
        "simple": textwrap.dedent(
            """\
                name: {name}
                # see https://documentation.ubuntu.com/rockcraft/en/stable/explanation/bases/
                # for more information about bases and using 'bare' bases for chiselled rocks
                base: ubuntu@22.04 # the base environment for this rock
                version: '0.1' # just for humans. Semantic versioning is recommended
                summary: Single-line elevator pitch for your amazing rock # 79 char long summary
                description: |
                    This is {name}'s description. You have a paragraph or two to tell the
                    most important story about it. Keep it under 100 words though,
                    we live in tweetspace and your description wants to look good in the
                    container registries out there.
                platforms: # the platforms this rock should be built on and run on
                    amd64:

                parts:
                    my-part:
                        plugin: nil
                """
        ),
        "flask-framework": textwrap.dedent(
            """\
                name: {name}
                # see https://documentation.ubuntu.com/rockcraft/en/stable/explanation/bases/
                # for more information about bases and using 'bare' bases for chiselled rocks
                base: ubuntu@22.04 # the base environment for this Flask application
                version: '0.1' # just for humans. Semantic versioning is recommended
                summary: A summary of your Flask application # 79 char long summary
                description: |
                    This is {name}'s description. You have a paragraph or two to tell the
                    most important story about it. Keep it under 100 words though,
                    we live in tweetspace and your description wants to look good in the
                    container registries out there.
                platforms: # The platforms this rock should be built on and run on
                    amd64:

                # to ensure the flask-framework extension works properly, your Flask application
                # should have an `app.py` file with an `app` object as the WSGI entrypoint.
                # A `requirements.txt` file with at least the flask package should also exist.
                # See https://documentation.ubuntu.com/rockcraft/en/stable/reference/extensions/flask-framework
                # for more information.
                extensions:
                    - flask-framework

                # Uncomment the sections you need and adjust according to your requirements.
                # parts:  # You need to uncomment this line to add or update any part.

                #   flask-framework/install-app:
                #     prime:
                #       # by default, only the files in app/, templates/, static/, and app.py
                #       # are copied into the image. You can modify the list below to override
                #       # the default list and include or exclude specific files/directories
                #       # in your project.
                #       # note: prefix each entry with "flask/app/" followed by the local path.
                #       - flask/app/.env
                #       - flask/app/app.py
                #       - flask/app/webapp
                #       - flask/app/templates
                #       - flask/app/static
                #       # You may need packages to build a python package. Add them here if necessary.
                #       build-packages:
                #           - pkg-config
                #           - libxmlsec1-dev

                # You can add package slices or Debian packages to the image.
                # Package slices are subsets of Debian packages, which result
                # in smaller and more secure images.
                # See https://documentation.ubuntu.com/rockcraft/en/latest/explanation/chisel/

                # Add this part if you want to add packages slices to your image.
                # You can find a list of packages slices in https://github.com/canonical/chisel-releases
                #   flask-framework/runtime-slices:
                #     plugin: nil
                #     stage-packages:
                #     # list required package slices for your flask application below.
                #     - libxml2_libs

                # If you want to add a Debian package to your image, add the next part
                #   flask-framework/runtime-debs:
                #     plugin: nil
                #     stage-packages:
                #     # list required Debian packages for your flask application below.
                #     - libpq-dev
                """
        ),
        "django-framework": textwrap.dedent(
            """\
                name: {name}
                # see https://documentation.ubuntu.com/rockcraft/en/stable/explanation/bases/
                # for more information about bases and using 'bare' bases for chiselled rocks
                base: ubuntu@22.04 # the base environment for this Django application
                version: '0.1' # just for humans. Semantic versioning is recommended
                summary: A summary of your Django application # 79 char long summary
                description: |
                    This is {name}'s description. You have a paragraph or two to tell the
                    most important story about it. Keep it under 100 words though,
                    we live in tweetspace and your description wants to look good in the
                    container registries out there.
                platforms: # The platforms this rock should be built on and run on
                    amd64:

                # to ensure the django-framework extension functions properly, your Django project
                # should have a structure similar to the following with ./{snake_name}/{snake_name}/wsgi.py
                # being the WSGI entry point and contain an application object.
                # +-- {snake_name}
                # |   |-- {snake_name}
                # |   |   |-- wsgi.py
                # |   |   +-- ...
                # |   |-- manage.py
                # |   |-- migrate.sh
                # |   +-- some_app
                # |       |-- views.py
                # |       +-- ...
                # |-- requirements.txt
                # +-- rockcraft.yaml

                extensions:
                    - django-framework

                # uncomment the sections you need and adjust according to your requirements.
                # parts:
                #   django-framework/dependencies:
                #     stage-packages:
                #       # list required packages or slices for your Django application below.
                #       - libpq-dev
            """
        ),
    }
    _DEFAULT_PROFILE = "simple"

    name = "init"
    help_msg = "Initialize a rockcraft project"
    overview = textwrap.dedent(
        """
        Initialize a rockcraft project by creating a minimalist,
        yet functional, rockcraft.yaml file in the current directory.
        """
    )

    def fill_parser(self, parser):
        """Specify command's specific parameters."""
        parser.add_argument(
            "--name", help="The name of the rock; defaults to the directory name"
        )
        parser.add_argument(
            "--profile",
            choices=list(self._INIT_TEMPLATES),
            default=self._DEFAULT_PROFILE,
            help=f"Use the specified project profile (defaults to '{self._DEFAULT_PROFILE}')",
        )

    @overrides
    def run(self, parsed_args: "argparse.Namespace") -> None:
        """Run the command."""
        name = parsed_args.name
        if name and not re.match(NAME_REGEX, name):
            raise errors.RockcraftInitError(
                f"'{name}' is not a valid rock name. " + INVALID_NAME_MESSAGE
            )

        if not name:
            name = pathlib.Path.cwd().name
            if not re.match(NAME_REGEX, name):
                name = "my-rock-name"
            emit.debug(f"Set project name to '{name}'")

        context = {"name": name, "snake_name": name.replace("-", "_").lower()}

        init(self._INIT_TEMPLATES[parsed_args.profile].format(**context))
