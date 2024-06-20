Getting started with Rockcraft for Flask
----------------------------------------

In this tutorial you will learn how to create a Flask application, build a rock
with the Flask application and run it.

Prerequisites
-------------
- snap enabled system (https://snapcraft.io)
- LXD installed (https://linuxcontainers.org/lxd/getting-started-cli/)
- Docker installed (https://snapcraft.io/docker)
- a text editor

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

The ``curl`` command should print ``Hello, world!`` in response.

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


Run the rock in Docker
----------------------

First, import the rock into Docker:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Now run the rock:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

The ``curl`` command should print ``Hello, world!`` in response.

Cleanup
-------

Stop the container and delete all the created files:

.. literalinclude:: code/getting-started-with-rockcraft-for-flask/task.yaml
    :language: bash
    :start-after: [docs:cleanup]
    :end-before: [docs:cleanup-end]
    :dedent: 2
