.. _init-web-app-rock:

Initialize a 12-factor app rock
*******************************

Use ``rockcraft init`` and specify the relevant profile:

.. code-block:: bash

    rockcraft init --profile <profile>

Rockcraft automatically creates a ``rockcraft.yaml`` project file
for the rock in your current directory. You will need to check the project
file to verify that the rock's name and description are correct.

.. seealso::

    :ref:`ref_commands_init`

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
