Using the flask extension
-------------------------

The Flask extension is compatible with the ``bare``, ``ubuntu:20.04``, and
``ubuntu:22.04`` bases. To employ it, include ``extensions: [flask]`` in your
``rockcraft.yaml`` file.

Example:

.. code-block:: yaml

    name: example-flask
    summary: Example.
    description: Example.
    version: "0.1"
    base: bare
    license: Apache-2.0

    extensions:
      - flask

Managing project files with the flask extension
-----------------------------------------------

By default, all files within the Flask project directory are copied, excluding
certain common files and directories, such as ``node_modules``. However,
this behaviour can be tailored to either specifically include or exclude files
from the Flask project directory in the ROCK image.

To include only select files from the project directory in the ROCK image,
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
