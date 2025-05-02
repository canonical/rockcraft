.. _init-config-web-app-rock:

Initialize and configure a 12-Factor app rock
*********************************************

The following how-to guide provides instructions on
initializing and configuring rocks for 12-factor apps.

Initialize a 12-factor app rock
-------------------------------

Use ``rockcraft init`` and specify the relevant profile:

.. code-block:: bash

    rockcraft init --profile <profile>

Rockcraft automatically creates a ``rockcraft.yaml`` project file
for the rock in your current directory. You will need to check the project
file to verify that the rock's name and description are correct.

.. tabs::

    .. group-tab:: Django

        .. code-block:: bash

            rockcraft init --profile django-framework

    .. group-tab:: ExpressJS

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

.. seealso::

    :ref:`ref_commands_init`

Include extra files in the OCI image
------------------------------------

The following files are included in the image by default from
the root of the project:

- ``app`` (does not apply to the ``go-framework``)
- ``app.py`` (does not apply to the ``go-framework``)
- ``migrate``
- ``migrate.sh``
- ``migrate.py`` (does not apply to the ``go-framework``)
- ``static``
- ``templates``

To change this list, add the following snippet to the project file:

.. tabs::

   .. group-tab:: Flask

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

      Note the ``flask/app/`` prefix that is required followed by the relative path to
      the project root.

   .. group-tab:: Django

      N/A

   .. group-tab:: FastAPI

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

      Note the ``app/`` prefix that is required followed by the relative path to
      the project root.

   .. group-tab:: Go

      .. code-block:: yaml
         :caption: rockcraft.yaml

           parts:
             go-framework/assets:
               prime:
                 - app/templates
                 - app/static
                 - app/migrate.sh

      Note the ``app/`` prefix that is required followed by the relative path to
      the project root.

Include additional debs in the OCI image
----------------------------------------

If your app requires debs -- for example, to connect to a database -- add the
following snippet to the project file:

.. tabs::

   .. group-tab:: Flask

      .. code-block:: yaml
         :caption: rockcraft.yaml

           parts:
             flask-framework/dependencies:
               stage-packages:
                 # list required packages or slices for your flask application below.
                 - libpq-dev

   .. group-tab:: Django

      .. code-block:: yaml
         :caption: rockcraft.yaml

           parts:
             django-framework/dependencies:
               stage-packages:
                 # list required packages or slices for your Django application below.
                 - libpq-dev

   .. group-tab:: FastAPI

      .. code-block:: yaml
         :caption: rockcraft.yaml

           parts:
             fastapi-framework/dependencies:
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

