.. meta::
    :description: How to initialize a rock for a 12-factor web app, and give it the minimal configuration needed for a supported framework.

.. _set-up-web-app-rock:

Set up a 12-Factor app rock
***************************

The following how-to guide provides instructions on
initializing and configuring rocks for 12-factor apps.

.. _set-up-web-app-rock-init:

Initialize a 12-factor app rock
-------------------------------

Use ``rockcraft init`` and specify the relevant profile:

.. code-block:: bash

    rockcraft init --profile <profile>

By default, Rockcraft initializes the project for Ubuntu 24.04 LTS. To
initialize it for another base, add the ``--base`` option:

.. code-block:: bash

    rockcraft init --profile <profile> --base ubuntu@26.04

Rockcraft automatically creates a ``rockcraft.yaml`` project file
for the rock in your current directory. You will need to check the project
file to verify that the rock's name and description are correct.

.. tabs::

    .. group-tab:: Django

        .. code-block:: bash

            rockcraft init --profile django-framework

    .. group-tab:: Express

        .. code-block:: bash

            rockcraft init --profile expressjs-framework

    .. group-tab:: FastAPI

        .. code-block:: bash

            rockcraft init --profile fastapi-framework

    .. group-tab:: Flask

        .. code-block:: bash

            rockcraft init --profile flask-framework

    .. group-tab:: Go

        .. code-block:: bash

            rockcraft init --profile go-framework

    .. group-tab:: Spring Boot

        .. code-block:: bash

            rockcraft init --profile spring-boot-framework


For more information, see: :ref:`ref_commands_init`

.. _set-up-web-app-rock-include-extra-files-oci:

Include extra files in the OCI image
------------------------------------

The files included in the image by default depend on the extension. For the
list of default files, see the "Included or excluded files" section of the
reference page for your framework:
:ref:`Flask <reference-flask-framework-prime>`,
:ref:`FastAPI <reference-fastapi-framework-prime>`,
:ref:`Go <reference-go-framework-stage>` and
:ref:`Spring Boot <reference-spring-boot-framework-stage>`.
The Django extension includes the whole Django project directory, except for
the ``db.sqlite3`` file. The Flask and FastAPI extensions include only the
default files, so list any other files your app needs, such as additional
Python modules, in the ``prime`` key.

.. note::
   Part names added by extensions vary by Ubuntu version. On Ubuntu 22.04 LTS
   and Ubuntu 24.04 LTS, write ``extension/part``; on Ubuntu 26.04 LTS,
   write ``extension.part``. For rocks with ``base: bare``, follow the
   convention for the configured ``build-base``.

For ``expressjs-framework``, place the migration script in the application
directory instead; see :ref:`reference-express-framework-migration`.

To change this list, add the following snippet to the project file:

.. tabs::

   .. group-tab:: Flask

      .. tab-set::

         .. tab-item:: Ubuntu 22.04 LTS and Ubuntu 24.04 LTS
            :sync: base-22-24

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 flask-framework/install-app:
                   prime:
                     - flask/app/.env
                     - flask/app/app.py
                     - flask/app/webapp
                     - flask/app/templates
                     - flask/app/static

            Note the ``flask/app/`` prefix that is required followed by the
            relative path to the project root.

         .. tab-item:: Ubuntu 26.04 LTS
            :sync: base-26-plus

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 flask-framework.install-app:
                   prime:
                     - app/.env
                     - app/app.py
                     - app/webapp
                     - app/templates
                     - app/static

            Note the ``app/`` prefix that is required followed by the relative
            path to the project root.

   .. group-tab:: Django

      N/A

   .. group-tab:: Express

      .. tab-set::

         .. tab-item:: Ubuntu 24.04 LTS
            :sync: base-24

            The entire ``app`` directory is copied into the rock, except for the
            files left out by the ``files`` array in ``package.json`` or by a
            ``.npmignore`` file. Place any additional files in the ``app``
            directory.

         .. tab-item:: Ubuntu 26.04 LTS
            :sync: base-26-plus

            The entire directory containing the ``package.json`` file is copied
            into the rock, except for the files left out by the ``files`` array
            in ``package.json`` or by a ``.npmignore`` file. Place any
            additional files in the same directory as ``package.json``.

   .. group-tab:: FastAPI

      .. tab-set::

         .. tab-item:: Ubuntu 24.04 LTS
            :sync: base-24

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 fastapi-framework/install-app:
                   prime:
                     - app/.env
                     - app/app.py
                     - app/webapp
                     - app/templates
                     - app/static

            Note the ``app/`` prefix that is required followed by the relative
            path to the project root.

         .. tab-item:: Ubuntu 26.04 LTS
            :sync: base-26-plus

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 fastapi-framework.install-app:
                   prime:
                     - app/.env
                     - app/app.py
                     - app/webapp
                     - app/templates
                     - app/static

            Note the ``app/`` prefix that is required followed by the relative
            path to the project root.

   .. group-tab:: Go

      .. tab-set::

         .. tab-item:: Ubuntu 24.04 LTS
            :sync: base-24

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 go-framework/assets:
                   stage:
                     - app/templates
                     - app/static
                     - app/migrate.sh

            Note the ``app/`` prefix that is required followed by the relative
            path to the project root.

         .. tab-item:: Ubuntu 26.04 LTS
            :sync: base-26-plus

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 go-framework.assets:
                   stage:
                     - app/templates
                     - app/static
                     - app/migrate.sh

            Note the ``app/`` prefix that is required followed by the relative
            path to the project root.

   .. group-tab:: Spring Boot

      .. tab-set::

         .. tab-item:: Ubuntu 24.04 LTS
            :sync: base-24

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 spring-boot-framework/assets:
                   stage:
                     - app/migrate.sh
                     - app/another_file_or_directory

            Note the ``app/`` prefix that is required followed by the relative
            path to the project root.

         .. tab-item:: Ubuntu 26.04 LTS
            :sync: base-26-plus

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 spring-boot-framework.assets:
                   stage:
                     - app/migrate.sh
                     - app/another_file_or_directory

            Note the ``app/`` prefix that is required followed by the relative
            path to the project root.

.. _set-up-web-app-rock-include-extra-debs-oci:

Include additional debs in the OCI image
----------------------------------------

If your app requires debs -- for example, to connect to a database -- add the
following snippet to the project file.

The Flask, Django and FastAPI snippets use debs, which work with an Ubuntu base
such as ``ubuntu@24.04``. For a rock with ``base: bare``, the extension already
lists slices in ``stage-packages``, and a part can't mix debs and slices. In
that case, list slices instead, for example ``libpq5_libs`` instead of
``libpq-dev``.

.. tabs::

   .. group-tab:: Flask

      .. tab-set::

         .. tab-item:: Ubuntu 22.04 LTS and Ubuntu 24.04 LTS
            :sync: base-22-24

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 flask-framework/dependencies:
                   stage-packages:
                     # list required packages or slices for your Flask application below.
                     - libpq-dev

         .. tab-item:: Ubuntu 26.04 LTS
            :sync: base-26-plus

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 flask-framework.dependencies:
                   stage-packages:
                     # list required packages or slices for your Flask application below.
                     - libpq-dev

   .. group-tab:: Django

      .. tab-set::

         .. tab-item:: Ubuntu 22.04 LTS and Ubuntu 24.04 LTS
            :sync: base-22-24

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 django-framework/dependencies:
                   stage-packages:
                     # list required packages or slices for your Django application below.
                     - libpq-dev

         .. tab-item:: Ubuntu 26.04 LTS
            :sync: base-26-plus

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 django-framework.dependencies:
                   stage-packages:
                     # list required packages or slices for your Django application below.
                     - libpq-dev

   .. group-tab:: FastAPI

      .. tab-set::

         .. tab-item:: Ubuntu 24.04 LTS
            :sync: base-24

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 fastapi-framework/dependencies:
                   stage-packages:
                     # list required packages or slices for your FastAPI application below.
                     - libpq-dev

         .. tab-item:: Ubuntu 26.04 LTS
            :sync: base-26-plus

            .. code-block:: yaml
               :caption: rockcraft.yaml

               parts:
                 fastapi-framework.dependencies:
                   stage-packages:
                     # list required packages or slices for your FastAPI application below.
                     - libpq-dev

   .. group-tab:: Go

      .. code-block:: yaml
         :caption: rockcraft.yaml

         parts:
           runtime-debs:
             plugin: nil
             stage-packages:
               - postgresql-client

      For the ``go-framework`` extension, a deb could be needed for example to use an external command in the migration process.

   .. group-tab:: Express

      The extension doesn't provide a dedicated part for additional packages.
      Add your own part instead:

      .. code-block:: yaml
         :caption: rockcraft.yaml

         parts:
           runtime-debs:
             plugin: nil
             stage-packages:
               - postgresql-client

.. _set-up-web-app-rock-override-commands:

Override commands
-----------------

The ``services`` key follows the :external+pebble:ref:`Pebble layer specification
<layer-specification>` and defines the entrypoint to your app.
You can override the default service commands in ``rockcraft.yaml``.

To override a service's command, check the default service
entrypoint generated by the extension by running ``rockcraft expand-extensions``.
On Ubuntu 26.04 LTS, and for the Spring Boot extension on any base, this requires
the experimental extensions to be enabled; see :doc:`/reference/extensions/index`.
Then, adapt the command to your needs and declare it in your project file. For
example:

.. tabs::

   .. group-tab:: Flask

      .. tab-set::

         .. tab-item:: Ubuntu 22.04 LTS and Ubuntu 24.04 LTS
            :sync: base-22-24

            .. code-block:: yaml
               :caption: Output of ``rockcraft expand-extensions``

               # ...
               services:
                 flask:
                   override: replace
                   command: /bin/python3 -m gunicorn -c /flask/gunicorn.conf.py 'app:app' -k [ sync ]
                   startup: enabled
                   after:
                     - statsd-exporter
                   user: _daemon_

            To limit the maximum number of pending connections in Gunicorn to 1024, add the
            following lines to your project file.

            .. code-block:: yaml
               :caption: rockcraft.yaml

               services:
                 flask:
                   command: /bin/python3 -m gunicorn -c /flask/gunicorn.conf.py 'app:app' --backlog 1024 -k [ sync ]

         .. tab-item:: Ubuntu 26.04 LTS
            :sync: base-26-plus

            .. code-block:: yaml
               :caption: Output of ``rockcraft expand-extensions``

               # ...
               services:
                 flask:
                   override: replace
                   command: /bin/python3 -m gunicorn -c /var/lib/gunicorn/gunicorn.conf.py 'app:app' -k [ sync ]
                   startup: enabled
                   after:
                     - statsd-exporter
                   user: _daemon_

            To limit the maximum number of pending connections in Gunicorn to 1024, add the
            following lines to your project file.

            .. code-block:: yaml
               :caption: rockcraft.yaml

               services:
                 flask:
                   command: /bin/python3 -m gunicorn -c /var/lib/gunicorn/gunicorn.conf.py 'app:app' --backlog 1024 -k [ sync ]

   .. group-tab:: Django

      .. tab-set::

         .. tab-item:: Ubuntu 22.04 LTS and Ubuntu 24.04 LTS
            :sync: base-22-24

            .. code-block:: yaml
               :caption: Output of ``rockcraft expand-extensions``

               # ...
               services:
                 django:
                   override: replace
                   command: /bin/python3 -m gunicorn -c /django/gunicorn.conf.py 'django_hello_world.wsgi:application' -k [ sync ]
                   startup: enabled
                   after:
                     - statsd-exporter
                   user: _daemon_

            To limit the maximum number of pending connections in ``Gunicorn`` to 1024, add the following
            lines to ``rockcraft.yaml``.

            .. code-block:: yaml
               :caption: rockcraft.yaml

               services:
                 django:
                   command: /bin/python3 -m gunicorn -c /django/gunicorn.conf.py 'django_hello_world.wsgi:application' --backlog 1024 -k [ sync ]

         .. tab-item:: Ubuntu 26.04 LTS
            :sync: base-26-plus

            .. code-block:: yaml
               :caption: Output of ``rockcraft expand-extensions``

               # ...
               services:
                 django:
                   override: replace
                   command: /bin/python3 -m gunicorn -c /var/lib/gunicorn/gunicorn.conf.py 'django_hello_world.wsgi:application' -k [ sync ]
                   startup: enabled
                   after:
                     - statsd-exporter
                   user: _daemon_

            To limit the maximum number of pending connections in ``Gunicorn`` to 1024, add the following
            lines to ``rockcraft.yaml``.

            .. code-block:: yaml
               :caption: rockcraft.yaml

               services:
                 django:
                   command: /bin/python3 -m gunicorn -c /var/lib/gunicorn/gunicorn.conf.py 'django_hello_world.wsgi:application' --backlog 1024 -k [ sync ]

   .. group-tab:: FastAPI

      .. code-block:: yaml
         :caption: Output of ``rockcraft expand-extensions``

         # ...
         services:
           fastapi:
             override: replace
             command: /bin/python3 -m uvicorn app:app
             startup: enabled
             environment:
               UVICORN_HOST: 0.0.0.0
             user: _daemon_
             working-dir: /app

      To limit the maximum number of pending connections in ``uvicorn`` to 1024, add the following
      lines to ``rockcraft.yaml``.

      .. code-block:: yaml
         :caption: rockcraft.yaml

         services:
           fastapi:
             command: /bin/python3 -m uvicorn app:app --backlog 1024

   .. group-tab:: Go

      .. code-block:: yaml
         :caption: Output of ``rockcraft expand-extensions``

         # ...
         services:
           go:
             override: replace
             command: go-hello-world
             startup: enabled
             user: _daemon_
             working-dir: /app

      To pass the argument ``--example-arg`` to the main Go app, add the following lines
      to ``rockcraft.yaml``.

      .. code-block:: yaml
         :caption: rockcraft.yaml

         services:
           go:
             override: replace
             command: go-hello-world --example-arg

   .. group-tab:: Express

      .. code-block:: yaml
         :caption: Output of ``rockcraft expand-extensions``

         # ...
         services:
           expressjs:
             override: replace
             command: npm start
             startup: enabled
             environment:
               NODE_ENV: production
             user: _daemon_
             working-dir: /app


      To pass the argument ``--example-arg`` to the ExpressJS script, add the following lines
      to ``rockcraft.yaml``.

      .. code-block:: yaml
         :caption: rockcraft.yaml

         services:
           expressjs:
             command: npm start -- --example-arg

   .. group-tab:: Spring Boot

      .. code-block:: yaml
         :caption: Output of ``rockcraft expand-extensions``

         # ...
         services:
           spring-boot:
             override: replace
             command: bash -c "java -jar *.jar"
             startup: enabled
             user: _daemon_
             working-dir: /app

      To enable a debug mode with a flag, add the following lines to ``rockcraft.yaml``.

      .. code-block:: yaml
         :caption: rockcraft.yaml

         services:
           spring-boot:
             command: bash -c "java -jar *.jar --debug"
