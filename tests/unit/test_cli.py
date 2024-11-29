# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021-2022 Canonical Ltd.
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
import pathlib
import sys
import textwrap
from pathlib import Path
from unittest.mock import DEFAULT, call

import pytest
import yaml
from craft_cli import emit
from rockcraft import cli, extensions, services
from rockcraft.application import APP_METADATA, Rockcraft
from rockcraft.models import project


def test_run_pack_services(mocker, monkeypatch, tmp_path):
    # Pretend it's running inside the managed instance
    monkeypatch.setenv("CRAFT_MANAGED_MODE", "1")

    log_path = tmp_path / "rockcraft.log"
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(Rockcraft, "get_project")
    mocker.patch.object(Rockcraft, "log_path", new=log_path)

    fake_prime_dir = Path("/fake/prime/dir")

    # Mock the relevant methods from the lifecycle and package services
    lifecycle_mocks = mocker.patch.multiple(
        services.RockcraftLifecycleService,
        setup=DEFAULT,
        prime_dir=fake_prime_dir,
        run=DEFAULT,
        project_info=DEFAULT,
    )

    package_mocks = mocker.patch.multiple(
        services.RockcraftPackageService, write_metadata=DEFAULT, pack=DEFAULT
    )

    command_line = ["rockcraft", "pack"]
    mocker.patch.object(sys, "argv", command_line)

    cli.run()

    lifecycle_mocks["run"].assert_called_once_with(step_name="prime")

    package_mocks["write_metadata"].assert_called_once_with(fake_prime_dir)
    package_mocks["pack"].assert_called_once_with(fake_prime_dir, Path())

    assert mock_ended_ok.called
    assert log_path.is_file()


@pytest.fixture
def valid_dir(new_dir, monkeypatch):
    valid = pathlib.Path(new_dir) / "valid"
    valid.mkdir()
    monkeypatch.chdir(valid)


@pytest.mark.usefixtures("valid_dir")
def test_run_init(mocker):
    mock_ended_ok = mocker.spy(emit, "ended_ok")
    mocker.patch.object(sys, "argv", ["rockcraft", "init"])

    cli.run()

    rockcraft_yaml_path = Path("rockcraft.yaml")
    rock_project = project.Project.unmarshal(
        yaml.safe_load(rockcraft_yaml_path.read_text())
    )

    assert len(rock_project.summary) < 80
    assert len(rock_project.description.split()) < 100
    assert mock_ended_ok.mock_calls == [call()]


@pytest.mark.usefixtures("valid_dir")
def test_run_init_with_name(mocker):
    mocker.patch.object(sys, "argv", ["rockcraft", "init", "--name=foobar"])

    cli.run()

    rockcraft_yaml_path = Path("rockcraft.yaml")
    rock_project = project.Project.unmarshal(
        yaml.safe_load(rockcraft_yaml_path.read_text())
    )

    assert rock_project.name == "foobar"


@pytest.mark.usefixtures("valid_dir")
def test_run_init_with_invalid_name(mocker):
    mocker.patch.object(sys, "argv", ["rockcraft", "init", "--name=f"])
    return_code = cli.run()
    assert return_code == 1


def test_run_init_fallback_name(mocker, new_dir, monkeypatch):
    mocker.patch.object(sys, "argv", ["rockcraft", "init"])
    invalid_dir = pathlib.Path(new_dir) / "f"
    invalid_dir.mkdir()
    monkeypatch.chdir(invalid_dir)

    cli.run()

    rockcraft_yaml_path = invalid_dir / "rockcraft.yaml"
    rock_project = project.Project.unmarshal(
        yaml.safe_load(rockcraft_yaml_path.read_text())
    )

    assert rock_project.name == "my-rock-name"


def test_run_init_flask(mocker, emitter, monkeypatch, new_dir, tmp_path):
    (new_dir / "requirements.txt").write_text("Flask", encoding="utf-8")
    (new_dir / "app.py").write_text("app = object()", encoding="utf-8")

    mocker.patch.object(
        sys,
        "argv",
        ["rockcraft", "init", "--profile=flask-framework", "--name", "test-name"],
    )

    cli.run()

    versioned_url = APP_METADATA.versioned_docs_url

    rockcraft_yaml_path = Path("rockcraft.yaml")
    rock_project_yaml = yaml.safe_load(rockcraft_yaml_path.read_text())

    assert len(rock_project_yaml["summary"]) < 80
    assert len(rock_project_yaml["description"].split()) < 100
    assert rockcraft_yaml_path.read_text() == textwrap.dedent(
        f"""\
            name: test-name
            # see {versioned_url}/explanation/bases/
            # for more information about bases and using 'bare' bases for chiselled rocks
            base: ubuntu@22.04 # the base environment for this Flask application
            version: '0.1' # just for humans. Semantic versioning is recommended
            summary: A summary of your Flask application # 79 char long summary
            description: |
                This is test-name's description. You have a paragraph or two to tell the
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
            #       # by default, only the files in app/, templates/, static/, migrate, migrate.sh,
            #       # migrate.py and app.py are copied into the image. You can modify the list
            #       # below to override the default list and include or exclude specific
            #       # files/directories in your project.
            #       # note: prefix each entry with "flask/app/" followed by the local path.
            #       - flask/app/.env
            #       - flask/app/app.py
            #       - flask/app/webapp
            #       - flask/app/templates
            #       - flask/app/static

            # you may need Ubuntu packages to build a python dependency. Add them here if necessary.
            #   flask-framework/dependencies:
            #     build-packages:
            #       # for example, if you need pkg-config and libxmlsec1-dev to build one
            #       # of your packages:
            #       - pkg-config
            #       - libxmlsec1-dev

            # uncomment this section to enable the async workers for Gunicorn.
            #   flask-framework/async-dependencies:
            #     python-packages:
            #       - gunicorn[gevent]

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
    )
    emitter.assert_message(
        textwrap.dedent(
            f"""\
        Go to {versioned_url}/reference/extensions/flask-framework to read more about the 'flask-framework' profile."""
        )
    )
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "0")
    project.Project.unmarshal(extensions.apply_extensions(tmp_path, rock_project_yaml))


def test_run_init_django(mocker, emitter, monkeypatch, new_dir, tmp_path):
    (new_dir / "requirements.txt").write_text("Django", encoding="utf-8")
    new_dir.mkdir("test_name")
    new_dir.mkdir("test_name/test_name")
    (new_dir / "test_name/manage.py").write_text(
        """\
        #!/usr/bin/env python
        \"\"\"Django's command-line utility for administrative tasks.\"\"\"
        import os
        import sys


        def main():
            \"\"\"Run administrative tasks.\"\"\"
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_name.settings')
            try:
                from django.core.management import execute_from_command_line
            except ImportError as exc:
                raise ImportError(
                    \"Couldn't import Django. Are you sure it's installed and \"
                    \"available on your PYTHONPATH environment variable? Did you \"
                    \"forget to activate a virtual environment?\"
                ) from exc
            execute_from_command_line(sys.argv)


        if __name__ == '__main__':
            main()

        """,
        encoding="utf-8",
    )
    (new_dir / "test_name/test_name/urls.py").write_text(
        """\
            from django.contrib import admin
            from django.urls import path

            urlpatterns = [
                path('admin/', admin.site.urls),
            ]
        """,
        encoding="utf-8",
    )
    (new_dir / "test_name/test_name/__init__.py").write_text("", encoding="utf-8")
    (new_dir / "test_name/test_name/settings.py").write_text(
        """\
            \"\"\"
            Django settings for test_name project.

            Generated by 'django-admin startproject' using Django 5.1.3.

            For more information on this file, see
            https://docs.djangoproject.com/en/5.1/topics/settings/

            For the full list of settings and their values, see
            https://docs.djangoproject.com/en/5.1/ref/settings/
            \"\"\"

            from pathlib import Path

            # Build paths inside the project like this: BASE_DIR / 'subdir'.
            BASE_DIR = Path(__file__).resolve().parent.parent


            # Quick-start development settings - unsuitable for production
            # See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

            # SECURITY WARNING: keep the secret key used in production secret!
            SECRET_KEY = 'django-insecure-s!661fk_mhkv!thlq1j&o+%7&%(djz+ir=6^+o$jtgbf(_2t_s'

            # SECURITY WARNING: don't run with debug turned on in production!
            DEBUG = True

            ALLOWED_HOSTS = []


            # Application definition

            INSTALLED_APPS = [
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
            ]

            MIDDLEWARE = [
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.clickjacking.XFrameOptionsMiddleware',
            ]

            ROOT_URLCONF = 'test_name.urls'

            TEMPLATES = [
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [],
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'context_processors': [
                            'django.template.context_processors.debug',
                            'django.template.context_processors.request',
                            'django.contrib.auth.context_processors.auth',
                            'django.contrib.messages.context_processors.messages',
                        ],
                    },
                },
            ]

            WSGI_APPLICATION = 'test_name.wsgi.application'


            # Database
            # https://docs.djangoproject.com/en/5.1/ref/settings/#databases

            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / 'db.sqlite3',
                }
            }


            # Password validation
            # https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

            AUTH_PASSWORD_VALIDATORS = [
                {
                    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
                },
                {
                    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
                },
                {
                    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
                },
                {
                    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
                },
            ]


            # Internationalization
            # https://docs.djangoproject.com/en/5.1/topics/i18n/

            LANGUAGE_CODE = 'en-us'

            TIME_ZONE = 'UTC'

            USE_I18N = True

            USE_TZ = True


            # Static files (CSS, JavaScript, Images)
            # https://docs.djangoproject.com/en/5.1/howto/static-files/

            STATIC_URL = 'static/'

            # Default primary key field type
            # https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

            DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
        """,
        encoding="utf-8",
    )

    (new_dir / "test_name/test_name/wsgi.py").write_text(
        "import os\nfrom django.core.wsgi import get_wsgi_application\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')\napplication = get_wsgi_application()\n",
        encoding="utf-8",
    )
    mocker.patch.object(
        sys,
        "argv",
        ["rockcraft", "init", "--profile=django-framework", "--name", "test-name"],
    )

    cli.run()

    versioned_url = APP_METADATA.versioned_docs_url

    rockcraft_yaml_path = Path("rockcraft.yaml")
    rock_project_yaml = yaml.safe_load(rockcraft_yaml_path.read_text())

    assert len(rock_project_yaml["summary"]) < 80
    assert len(rock_project_yaml["description"].split()) < 100
    assert rockcraft_yaml_path.read_text() == textwrap.dedent(
        f"""\
                name: test-name
                # see {versioned_url}/explanation/bases/
                # for more information about bases and using 'bare' bases for chiselled rocks
                base: ubuntu@22.04 # the base environment for this Django application
                version: '0.1' # just for humans. Semantic versioning is recommended
                summary: A summary of your Django application # 79 char long summary
                description: |
                    This is test-name's description. You have a paragraph or two to tell the
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
                # should have a structure similar to the following with ./test_name/test_name/wsgi.py
                # being the WSGI entry point and contain an application object.
                # +-- test_name
                # |   |-- test_name
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

                # uncomment this section to enable the async workers for Gunicorn.
                #   django-framework/async-dependencies:
                #     python-packages:
                #       - gunicorn[gevent]

        """
    )
    emitter.assert_message(
        textwrap.dedent(
            """\
        Created 'rockcraft.yaml'."""
        )
    )
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "0")
    project.Project.unmarshal(extensions.apply_extensions(tmp_path, rock_project_yaml))
    project.Project.unmarshal(extensions.apply_extensions(tmp_path, rock_project_yaml))
    project.Project.unmarshal(extensions.apply_extensions(tmp_path, rock_project_yaml))
