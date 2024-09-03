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

import argparse
import pathlib
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path

from craft_application.commands import AppCommand
from craft_cli import emit
from overrides import overrides  # type: ignore[reportUnknownVariableType]

from rockcraft import errors
from rockcraft.models.project import MESSAGE_INVALID_NAME, PROJECT_NAME_REGEX


def init(rockcraft_yaml_content: str) -> Path:
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

    return rockcraft_yaml_path


@dataclass
class _InitProfile:
    rockcraft_yaml: str
    doc_slug: str | None = None


class InitCommand(AppCommand):
    """Initialize a rockcraft project."""

    _PROFILES = {
        "simple": _InitProfile(
            rockcraft_yaml=textwrap.dedent(
                """\
                name: {name}
                # see {versioned_url}/explanation/bases/
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
            )
        ),
        "flask-framework": _InitProfile(
            rockcraft_yaml=textwrap.dedent(
                """\
                name: {name}
                # see {versioned_url}/explanation/bases/
                # for more information about bases and using 'bare' bases for chiselled rocks
                base: ubuntu@22.04 # the base environment for this Flask application
                version: '0.1' # just for humans. Semantic versioning is recommended
                summary: A summary of your Flask application # 79 char long summary
                description: |
                    This is {name}'s description. You have a paragraph or two to tell the
                    most important story about it. Keep it under 100 words though,
                    we live in tweetspace and your description wants to look good in the
                    container registries out there.
                # the platforms this rock should be built on and run on.
                # you can check your architecture with `dpkg --print-architecture`
                platforms:
                    amd64:
                    # arm64:
                    # ppc64el:
                    # s390x:

                # to ensure the flask-framework extension works properly, your Flask application
                # should have an `app.py` file with an `app` object as the WSGI entrypoint.
                # a `requirements.txt` file with at least the flask package should also exist.
                # see {versioned_url}/reference/extensions/flask-framework
                # for more information.
                extensions:
                    - flask-framework

                # uncomment the sections you need and adjust according to your requirements.
                # parts:  # you need to uncomment this line to add or update any part.

                #   flask-framework/install-app:
                #     prime:
                #       # by default, only the files in app/, templates/, static/, migrate,
                #       # migrate.sh and app.py are copied into the image. You can modify the list
                #       # below to override the default list and include or exclude specific
                #       # files/directories in your project.
                #       # note: prefix each entry with "flask/app/" followed by the local path.
                #       - flask/app/.env
                #       - flask/app/app.py
                #       - flask/app/webapp
                #       - flask/app/templates
                #       - flask/app/static

                # you may need packages to build a python package. Add them here if necessary.
                #   flask-framework/dependencies:
                #     build-packages:
                #       # for example, if you need pkg-config and libxmlsec1-dev to build one
                #       # of your packages:
                #       - pkg-config
                #       - libxmlsec1-dev

                # you can add package slices or Debian packages to the image.
                # package slices are subsets of Debian packages, which result
                # in smaller and more secure images.
                # see {versioned_url}/explanation/chisel/

                # add this part if you want to add packages slices to your image.
                # you can find a list of packages slices at https://github.com/canonical/chisel-releases
                #   runtime-slices:
                #     plugin: nil
                #     stage-packages:
                #       # list the required package slices for your flask application below.
                #       # for example, for the slice libs of libpq5:
                #       - libpq5_libs

                # if you want to add a Debian package to your image, add the next part
                #   runtime-debs:
                #     plugin: nil
                #     stage-packages:
                #       # list required Debian packages for your flask application below.
                #       - libpq5
                """
            ),
            doc_slug="/reference/extensions/flask-framework",
        ),
        "django-framework": _InitProfile(
            rockcraft_yaml=textwrap.dedent(
                """\
                name: {name}
                # see {versioned_url}/explanation/bases/
                # for more information about bases and using 'bare' bases for chiselled rocks
                base: ubuntu@22.04 # the base environment for this Django application
                version: '0.1' # just for humans. Semantic versioning is recommended
                summary: A summary of your Django application # 79 char long summary
                description: |
                    This is {name}'s description. You have a paragraph or two to tell the
                    most important story about it. Keep it under 100 words though,
                    we live in tweetspace and your description wants to look good in the
                    container registries out there.
                # the platforms this rock should be built on and run on.
                # you can check your architecture with `dpkg --print-architecture`
                platforms:
                    amd64:
                    # arm64:
                    # ppc64el:
                    # s390x:

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
            )
        ),
        "go-framework": _InitProfile(
            rockcraft_yaml=textwrap.dedent(
                """\
                name: {name}
                # see {versioned_url}/explanation/bases/
                # for more information about bases and using 'bare' bases for chiselled rocks
                base: bare # as an alternative, a ubuntu base can be used
                build-base: ubuntu@24.04 # build-base is required when the base is bare
                version: '0.1' # just for humans. Semantic versioning is recommended
                summary: A summary of your Go application # 79 char long summary
                description: |
                    This is {name}'s description. You have a paragraph or two to tell the
                    most important story about it. Keep it under 100 words though,
                    we live in tweetspace and your description wants to look good in the
                    container registries out there.
                # the platforms this rock should be built on and run on.
                # you can check your architecture with `dpkg --print-architecture`
                platforms:
                    amd64:
                    # arm64:
                    # ppc64el:
                    # s390x:

                # to ensure the go-framework extension functions properly, your Go project
                # should have a go.mod file. Check the parts section for the selection of
                # the default binary.
                # see {versioned_url}/reference/extensions/go-framework
                # for more information.
                # +-- {snake_name}
                # |   |-- go.mod
                # |   |-- migrate.sh

                extensions:
                    - go-framework

                # uncomment the sections you need and adjust according to your requirements.
                # parts:

                #   go-framework/install-app:
                #    # select a specific Go version. Otherwise the current stable one will be used.
                #    build-snaps:
                #    - go/1.22/stable
                #    organize:
                #    # if the main package is in the base directory and the rockcraft name
                #    # attribute is equal to the go module name, the name of the server will
                #    # be selected correctly, otherwise you can adjust it.
                #    # the file in /usr/local/bin/ with the name of the rockcraft project will be
                #    # the binary to run your server.
                #    # you can also include here other binary files to be included in the rock.
                #      bin/otherbinary: usr/local/bin/projectname

                #   go-framework/assets:
                #     stage:
                #       # by default, only the files in templates/ and static/
                #       # are copied into the image. You can modify the list below to override
                #       # the default list and include or exclude specific files/directories
                #       # in your project.
                #       # note: Prefix each entry with "app/" followed by the local path.
                #       - app/templates
                #       - app/static
                #       - app/otherdirectory
                #       - app/otherfile
            """
            )
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

    def fill_parser(self, parser: argparse.ArgumentParser) -> None:
        """Specify command's specific parameters."""
        parser.add_argument(
            "--name", help="The name of the rock; defaults to the directory name"
        )
        parser.add_argument(
            "--profile",
            choices=list(self._PROFILES),
            default=self._DEFAULT_PROFILE,
            help=f"Use the specified project profile (defaults to '{self._DEFAULT_PROFILE}')",
        )

    @overrides
    def run(self, parsed_args: "argparse.Namespace") -> None:
        """Run the command."""
        name = parsed_args.name
        if name and not re.match(PROJECT_NAME_REGEX, name):
            raise errors.RockcraftInitError(
                f"'{name}' is not a valid rock name. " + MESSAGE_INVALID_NAME
            )

        if not name:
            name = pathlib.Path.cwd().name
            if not re.match(PROJECT_NAME_REGEX, name):
                name = "my-rock-name"
            emit.debug(f"Set project name to '{name}'")

        # Get the init profile
        init_profile = self._PROFILES[parsed_args.profile]

        versioned_docs_url = self._app.versioned_docs_url

        # Setup the reference documentation link if available
        profile_reference_docs: str | None = None
        if versioned_docs_url and init_profile.doc_slug:
            profile_reference_docs = versioned_docs_url + init_profile.doc_slug

        # Format the template, all templates should be tested to avoid risk of
        # expecting documentation when there isn't any set
        context = {
            "name": name,
            "snake_name": name.replace("-", "_").lower(),
            "profile_reference_docs": profile_reference_docs,
            "versioned_url": versioned_docs_url,
        }
        rockcraft_yaml_path = init(init_profile.rockcraft_yaml.format(**context))

        message = f"Created {str(rockcraft_yaml_path)!r}."
        if profile_reference_docs:
            message += (
                f"\nGo to {profile_reference_docs} to read more about the "
                f"{parsed_args.profile!r} profile."
            )
        emit.message(message)
