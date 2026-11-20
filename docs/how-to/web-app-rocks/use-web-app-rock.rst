.. meta::
    :description: How to deploy and update a rock of a 12-factor web app. This guide  demonstrates using Juju as a software orchestrator that consumes the rock.

.. _use-web-app-rock:

Use a 12-factor app rock
************************

The following how-to guide provides instructions on
using rocks for 12-factor apps.

.. note::

   The Ubuntu 26.04 LTS extensions, and the Spring Boot extension on any base,
   are experimental. To use them, set
   ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1`` when running
   ``rockcraft pack``. For details, see
   :ref:`reference-extensions-ubuntu-2604-frameworks`.

.. _use-web-app-rock-update-deploy-oci:

Update and deploy the OCI image
-------------------------------

.. tabs::

   .. group-tab:: Flask

      After making a change to your app:

      1. Include any new files in the new OCI image, as
         described in :ref:`set-up-web-app-rock-include-extra-files-oci`.
      2. Run ``rockcraft pack`` to create the new OCI image.
      3. To upload the OCI image to the local Docker registry, run:

         .. code-block:: bash

            rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false \
            oci-archive:<path to rock file> \
            docker://localhost:32000/<rock name>:<rock version>

      4. To deploy the new OCI image, run:

         .. tab-set::

            .. tab-item:: Ubuntu 22.04 LTS and Ubuntu 24.04 LTS
               :sync: base-22-24

               .. code-block:: bash

                  juju refresh <app name> --path=<relative path to .charm file> \
                  --resource flask-app-image=<localhost:32000/<rock name>:<rock version>>

            .. tab-item:: Ubuntu 26.04 LTS
               :sync: base-26-plus

               .. code-block:: bash

                  juju refresh <app name> --path=<relative path to .charm file> \
                  --resource app-image=<localhost:32000/<rock name>:<rock version>>

   .. group-tab:: Django

      After making a change to your app:

      1. Include any new files in the new OCI image, as
         described in :ref:`set-up-web-app-rock-include-extra-files-oci`.
      2. Run ``rockcraft pack`` to create the new OCI image.
      3. To upload the OCI image to the local Docker registry, run:

         .. code-block:: bash

            rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false \
            oci-archive:<path to rock file> \
            docker://localhost:32000/<rock name>:<rock version>

      4. To deploy the new OCI image, run:

         .. tab-set::

            .. tab-item:: Ubuntu 22.04 LTS and Ubuntu 24.04 LTS
               :sync: base-22-24

               .. code-block:: bash

                  juju refresh <app name> --path=<relative path to .charm file> \
                  --resource django-app-image=<localhost:32000/<rock name>:<rock version>>

            .. tab-item:: Ubuntu 26.04 LTS
               :sync: base-26-plus

               .. code-block:: bash

                  juju refresh <app name> --path=<relative path to .charm file> \
                  --resource app-image=<localhost:32000/<rock name>:<rock version>>

   .. group-tab:: FastAPI

      After making a change to your app:

      1. Include any new files in the new OCI image, as
         described in :ref:`set-up-web-app-rock-include-extra-files-oci`.
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

      1. Include any new files in the new OCI image, as
         described in :ref:`set-up-web-app-rock-include-extra-files-oci`.
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

   .. group-tab:: Express

      After making a change to your app:

      1. Include any new files in the new OCI image, as
         described in :ref:`set-up-web-app-rock-include-extra-files-oci`.
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

   .. group-tab:: Spring Boot

      After making a change to your app:

      1. Include any new files in the new OCI image, as
         described in :ref:`set-up-web-app-rock-include-extra-files-oci`.
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
