How to use a 12-factor app rock
*******************************

The following how-to guide provides instructions on
using rocks for 12-factor apps.

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
