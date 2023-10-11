Using the flask-framework extension
-----------------------------------

The Flask extension is compatible with the ``bare`` and ``ubuntu:22.04`` bases.
To employ it, include ``extensions: [ flask-framework ]`` in your
``rockcraft.yaml`` file.

Example:

.. code-block:: yaml

    name: example-flask
    summary: A Flask application
    description: A ROCK packing a Flask application via the flask extension
    version: "0.1"
    base: bare
    license: Apache-2.0

    extensions:
      - flask-framework

Managing project files with the flask extension
-----------------------------------------------

By default the flask extension only includes the ``app.py``, ``static``,
and ``templates`` in the flask project. But you can overwrite this behaviour
with a prime declaration in the specially-named ``flask/install-app``
part to instruct the flask extension on which files to include or exclude
from the project directory in the ROCK image.

The extension places the files from the project folder in the ``/flask/app``
directory in the final image - therefore, all inclusions and exclusions must
be prefixed with ``flask/app``.

For example, to include only select files:

.. code-block:: yaml

    flask/install-app:
      prime:
        - flask/app/static
        - flask/app/.env
        - flask/app/app.py
        - flask/app/templates

To exclude certain files from the project directory in the rock image,
add the following part to ``rockcraft.yaml``:

.. code-block:: yaml

    flask/install-app:
      prime:
        - -flask/app/.git
        - -flask/app/.venv
        - -flask/app/.yarn
        - -flask/app/node_modules
