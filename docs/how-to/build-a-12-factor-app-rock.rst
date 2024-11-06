How to build a 12-Factor app rock
*********************************

The following how-to guide provides instructions on managing
and configuring rocks for 12-factor applications.

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

To change this list, add the following snippet to the
``rockcraft.yaml``:

.. tabs::

   .. group-tab:: Flask

      .. code-block:: yaml

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
following snippet to ``rockcraft.yaml``:

.. tabs::

   .. group-tab:: Flask

      .. code-block:: yaml

           parts:
             flask-framework/dependencies:
               stage-packages:
                 # list required packages or slices for your flask application below.
                 - libpq-dev

   .. group-tab:: Django

      .. code-block:: yaml

           parts:
             django-framework/dependencies:
               stage-packages:
                 # list required packages or slices for your Django application below.
                 - libpq-dev

   .. group-tab:: FastAPI

      .. code-block:: yaml

           parts:
             fastapi-framework/dependencies:
               stage-packages:
                 # list required packages or slices for your FastAPI application below.
                 - libpq-dev

   .. group-tab:: Go

      .. code-block:: yaml

           parts:
             runtime-debs:
               plugin: nil
               stage-packages:
                 - postgresql-client

      For the ``go-framework`` extension, a deb could be needed for example to use an external command in the migration process.

Update and deploy the OCI image
-------------------------------

.. tabs::

   .. group-tab:: Flask

      After making a change to your app:

      1. Make sure that any new files will be included in the new OCI image.
      2. Run ``rockcraft pack`` to create the new OCI image.
      3. To upload the OCI image to the local Docker registry, run:

         .. code-block:: bash

            rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false \
            oci-archive:<path to rock file> \
            docker://localhost:32000/<rock name>:<rock version>

      4. To deploy the new OCI image, run:

         .. code-block:: bash

            juju refresh <app name> --path=<relative path to .charm file> \
            --resource flask-app-image=<localhost:32000/<rock name>:<rock version>>

   .. group-tab:: Django

      After making a change to your app:

      1. Make sure that any new files will be included in the new OCI image.
      2. Run ``rockcraft pack`` to create the new OCI image.
      3. To upload the OCI image to the local Docker registry, run:

         .. code-block:: bash

            rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false \
            oci-archive:<path to rock file> \
            docker://localhost:32000/<rock name>:<rock version>

      4. To deploy the new OCI image, run:

         .. code-block:: bash

            juju refresh <app name> --path=<relative path to .charm file> \
            --resource django-app-image=<localhost:32000/<rock name>:<rock version>>

   .. group-tab:: FastAPI

      After making a change to your app:

      1. Make sure that any new files will be included in the new OCI image.
      2. Run ``rockcraft pack`` to create the new OCI image.
      3. To upload the OCI image to the local Docker registry, run:

         .. code-block:: bash

            rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false \
            oci-archive:<path to rock file> \
            docker://localhost:32000/<rock name>:<rock version>

      4. To deploy the new OCI image, run:

         .. code-block:: bash

            juju refresh <app name> --path=<relative path to .charm file> \
            --resource app-image=<localhost:32000/<rock name>:<rock version>>

   .. group-tab:: Go

      After making a change to your app:

      1. Make sure that any new files will be included in the new OCI image.
      2. Run ``rockcraft pack`` to create the new OCI image.
      3. To upload the OCI image to the local Docker registry, run:

         .. code-block:: bash

            rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false \
            oci-archive:<path to rock file> \
            docker://localhost:32000/<rock name>:<rock version>

      4. To deploy the new OCI image, run:

         .. code-block:: bash

            juju refresh <app name> --path=<relative path to .charm file> \
            --resource app-image=<localhost:32000/<rock name>:<rock version>>
