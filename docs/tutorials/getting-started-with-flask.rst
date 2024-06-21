Getting started with Rockcraft for Flask
----------------------------------------

In this tutorial you will learn how to create a Flask application, build a rock
with the Flask application and run it.

Setup
=====

Start with a clean Ubuntu 22.04 installation. If you don't have one available,
you can create one using [multipass](https://multipass.run):

.. code-block:: bash

   sudo snap install multipass
   multipass launch --disk 10G --name flask-hello-world 22.04
   multipass shell flask-hello-world

LXD will be required for creating the OCI image. Make sure it is installed an
initialised:

.. code-block:: bash

   sudo snap install lxd
   lxd init --auto

Docker will be required to run the OCI image:

.. code-block:: bash

   sudo snap install docker

Rockcraft is required to create the OCI image:

.. code-block:: bash

   sudo snap install rockcraft --classic

Create a new directory for this tutorial and change into it:

.. code-block:: bash

   mkdir flask-hello-world
   cd flask-hello-world

Create Flask application
========================

Write the following into a text editor and save it as ``requirements.txt``:

.. literalinclude:: code/getting-started-with-flask/requirements.txt

Install ``python3-venv`` on your host and create a virtual environment:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:create-venv]
    :end-before: [docs:create-venv-end]
    :dedent: 2

In the same directory, write the following into a text editor and save it as
``app.py``:

.. literalinclude:: code/getting-started-with-flask/app.py
    :language: python

Run and test the flask application to verify everything is working:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:run-flask]
    :end-before: [docs:run-flask-end]
    :dedent: 2

Use ``curl`` to send a request to the root endpoint:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:request-flask]
    :end-before: [docs:request-flask-end]
    :dedent: 2

..  code-block:: text
    :class: log-snippets

    $ curl localhost:5000
    Hello, world!

Stop flask for now:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:stop-flask]
    :end-before: [docs:stop-flask-end]
    :dedent: 2

Create Flask rock
=================

Use the ``flask-framework`` profile to create ``rockcraft.yaml``:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

Open ``rockcraft.yaml`` in a text editor and customise the ``name``,
``summary``, ``description`` and ``license``. Ensure that ``platforms`` includes
the architecture of your host. For example, if your host uses the ARM
architecture, include ``arm64`` in ``platforms``. Pack the rock:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

Verify that the rock was created:

..  code-block:: text
    :class: log-snippets

    $ ls *.rock -l --block-size=MB
    -rw-r--r-- 1 ubuntu ubuntu 62MB Jun 21 13:09 flask-hello-world_0.1_amd64.rock

The created rock is around 62MB in size. This can be reduced which will be done
in a later part of this tutorial.

.. note::
    If you changed the ``name`` or ``version`` in ``rockcraft.yaml`` or are not
    on an ``amd64`` platform, the name of the ``.rock`` file will be different
    for you.

Run the rock in Docker
======================

Import the rock into Docker:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Check that the image was imported into Docker:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:verify-image]
    :end-before: [docs:verify-image-end]
    :dedent: 2

.. note::
    The size of the image reported by Docker is the uncompressed size which is
    larger than the size of the ``.rock`` file which is compressed.

Now run the rock:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use ``curl`` to send a request to the root endpoint:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:request-docker]
    :end-before: [docs:request-docker-end]
    :dedent: 2

..  code-block:: text
    :class: log-snippets

    $ curl localhost:8000
    Hello, world!

Stop the rock and remove the container and image for now:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2

Chisel the rock
===============

The size of the image can be reduced by using a ``bare`` base. In
``rockcraft.yaml``, change the ``base`` to ``bare`` and add a ``build-base`` of
``ubuntu@22.04``:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:change-base]
    :end-before: [docs:change-base-end]
    :dedent: 2

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:chisel-pack]
    :end-before: [docs:chisel-pack-end]
    :dedent: 2

Verify that the rock was created:

..  code-block:: text
    :class: log-snippets

    $ ls *.rock -l --block-size=MB
    -rw-r--r-- 1 ubuntu ubuntu 53MB Jun 21 13:25 flask-hello-world_0.1_amd64.rock

The created rock is now smaller at just 53MB in size. It can be run using Docker
using the same commands as before:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:docker-run-chisel]
    :end-before: [docs:docker-run-chisel-end]
    :dedent: 2

Use ``curl`` to send a request to the root endpoint:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:request-docker-chisel]
    :end-before: [docs:request-docker-chisel-end]
    :dedent: 2

..  code-block:: text
    :class: log-snippets

    $ curl localhost:8000
    Hello, world!

Stop the rock and remove the container and image for now:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-chisel]
    :end-before: [docs:stop-docker-chisel-end]
    :dedent: 2

Update Flask app
----------------

To update the app, for example, by adding a new ``/time`` endpoint which returns
the current time, open ``app.py`` in a text editor and update the code to:

.. literalinclude:: code/getting-started-with-flask/time-app.py
    :language: python

Open ``rockfile.yaml`` and change the ``version`` to ``0.2``. Pack and run the
rock using similar commands as before:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:docker-run-update]
    :end-before: [docs:docker-run-update-end]
    :dedent: 2

Use ``curl`` to send a request to the ``/time`` endpoint:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:request-docker-update]
    :end-before: [docs:request-docker-update-end]
    :dedent: 2

..  code-block:: text
    :class: log-snippets

    $ curl localhost:8000/time
    2024-06-21 03:42:38

Cleanup
=======

Stop the container and delete all the created files:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:cleanup]
    :end-before: [docs:cleanup-end]
    :dedent: 2
