Getting started with Rockcraft for Flask
----------------------------------------

In this tutorial you will learn how to create a Flask application, build a rock
with the Flask application and run it.

Prerequisites
-------------
- Ubuntu installed

Create Flask application
------------------------

Create a new directory and write the following into a text editor and save it as
``requirements.txt``:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/requirements.txt

Install `python3-venv` on your host and create a virtual environment:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/task.yaml
    :language: bash
    :start-after: [create-venv]
    :end-before: [create-venv-end]
    :dedent: 2

In the same directory, write the following into a text editor and save it as
``app.py``:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/app.py
    :language: python

Run and test the flask application to verify everything is working:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/task.yaml
    :language: bash
    :start-after: [run-flask]
    :end-before: [run-flask-end]
    :dedent: 2

Install Rockcraft
-----------------

Install Rockcraft on your host:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:install-rockcraft]
    :end-before: [docs:install-rockcraft-end]
    :dedent: 2

Create Flask rock
-----------------

Use the ``flask-framework`` profile to create ``rockcraft.yaml``:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/task.yaml
    :language: bash
    :start-after: [create-rockcraft-yaml]
    :end-before: [create-rockcraft-yaml-end]
    :dedent: 2

Open ``rockcraft.yaml`` in a text editor and customize the ``name``,
``summary``, ``description`` and ``license``. Ensure that ``platforms`` includes
the architecture of your host. For example, if your host uses the ARM
architecture, include ``arm64`` in ``platforms``. Pack the rock:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/task.yaml
    :language: bash
    :start-after: [pack]
    :end-before: [pack-end]
    :dedent: 2








.. note::
    The Flask extension is compatible with the ``bare`` and ``ubuntu@22.04``
    bases.

To employ it, include ``extensions: [ flask-framework ]`` in your
``rockcraft.yaml`` file.

Example:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/example/rockcraft.yaml
    :language: yaml

Managing project files with the flask extension
-----------------------------------------------

By default the flask extension only includes ``app.py``, ``static/``,
``app/``, and ``templates/`` in the flask project, but you can overwrite this
behaviour with a prime declaration in the specially-named
``flask-framework/install-app`` part to instruct the flask extension on which
files to include or exclude from the project directory in the rock image.

The extension places the files from the project folder in the ``/flask/app``
directory in the final image - therefore, all inclusions and exclusions must
be prefixed with ``flask/app``.

For example, to include only select files:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/prime_example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]

To exclude certain files from the project directory in the rock image,
add the following part to ``rockcraft.yaml``:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/prime_exclude_example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]
