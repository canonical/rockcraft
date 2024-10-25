How to build a 12-Factor app rock
*********************************

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

To change this, the following snippet needs to be added to
the ``rockcraft.yaml``:

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

      .. code-block:: yaml

           parts:
             django-framework/install-app:
               prime:
                 - django/app/.env
                 - django/app/app.py
                 - django/app/webapp
                 - django/app/templates
                 - django/app/static

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
following snippet to the ``rockcraft.yaml``:

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

      For the ``go-framework``, a deb could be needed for example to use an external command in the migration process.

Update the OCI image
--------------------

.. tabs ::

   .. group-tab:: Flask

      After making a change to your app:

      1. Make sure that any new files will be included in the new OCI image.
      2. Run ``rockcraft pack`` to create the new OCI image.
      3. Run ``rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false oci-archive:<path to rock file> docker://localhost:32000/<rock name>:<rock version>`` to upload the OCI image to the local Docker registry.
      4. Run ``juju refresh <app name> --path=<relative path to .charm file> --resource flask-app-image=<localhost:32000/<rock name>:<rock version>>`` to deploy the new OCI image.

   .. group-tab:: Django

      After making a change to your app:

      1. Make sure that any new files will be included in the new OCI image.
      2. Run ``rockcraft pack`` to create the new OCI image.
      3. Run ``rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false oci-archive:<path to rock file> docker://localhost:32000/<rock name>:<rock version>`` to upload the OCI image to the registry.
      4. Run ``juju refresh <app name> --path=<relative path to .charm file> --resource django-app-image=<localhost:32000/<rock name>:<rock version>>`` to deploy the new OCI image.

   .. group-tab:: FastAPI

      After making a change to your app:

      1. Make sure that any new files will be included in the new OCI image.
      2. Run ``rockcraft pack`` to create the new OCI image.
      3. Run ``rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false oci-archive:<path to rock file> docker://localhost:32000/<rock name>:<rock version>`` to upload the OCI image to the registry.
      4. Run ``juju refresh <app name> --path=<relative path to .charm file> --resource app-image=<localhost:32000/<rock name>:<rock version>>`` to deploy the new OCI image.

   .. group-tab:: Go

      After making a change to your app:

      1. Make sure that any new files will be included in the new OCI image.
      2. Run ``rockcraft pack`` to create the new OCI image.
      3. Run ``rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false oci-archive:<path to rock file> docker://localhost:32000/<rock name>:<rock version>`` to upload the OCI image to the registry.
      4. Run ``juju refresh <app name> --path=<relative path to .charm file> --resource app-image=<localhost:32000/<rock name>:<rock version>>`` to deploy the new OCI image.
