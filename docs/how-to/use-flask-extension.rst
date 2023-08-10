The Flask Extension
*******************

The Flask extension streamlines the process of building Flask application rocks.

It facilitates the installation of Flask application dependencies, including
Gunicorn, in the rock image. Additionally, it transfers your project files to
``/srv/flask/app`` within the rock image.

Using the Flask Extension
-------------------------

The Flask extension is compatible with ``bare``, ``ubuntu:20.04``, and
``ubuntu:22.04``. To employ it, include ``extensions: [flask]`` in your
``rockcraft.yaml`` file.

Example:

.. code-block:: yaml

    name: example
    summary: Example.
    description: Example.
    version: "0.1"
    base: bare
    license: Apache-2.0

    extensions:
      - flask

Managing Project Files with the Flask Extension
----------------------------------------------

By default, all files within the Flask project directory are copied, excluding
certain common files and directories, such as ``node_modules``. However,
this behavior can be tailored to either specifically include or exclude files
from the Flask project directory in the rock image.

To include only select files from the project directory in the rock image,
append the following part to ``rockcraft.yaml``:

.. code-block:: yaml

    flask/install-app:
      prime:
        - srv/flask/app/static
        - srv/flask/app/.env
        - srv/flask/app/webapp
        - srv/flask/app/templates

To exclude certain files from the project directory in the rock image,
add the following part to ``rockcraft.yaml``:

.. code-block:: yaml

    flask/install-app:
      prime:
        - -srv/flask/app/charmcraft.auth
