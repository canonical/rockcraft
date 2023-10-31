Bundle a Node.js app into a ROCK
********************************

This tutorial describes the steps needed to bundle a typical Node.js application
into a ROCK.

Prerequisites
-------------
- snap enabled system (https://snapcraft.io/docs/installing-snapd)
- LXD installed
  (https://documentation.ubuntu.com/lxd/en/latest/howto/initialize/)
- Docker installed (https://snapcraft.io/docker)
- a text editor


Install Rockcraft
-----------------

Install Rockcraft on your host:

.. literalinclude:: code/node-app/task.yaml
    :language: bash
    :start-after: [docs:install-rockcraft]
    :end-before: [docs:install-rockcraft-end]
    :dedent: 2


Project Setup
-------------

Starting in an empty folder, create a ``src/`` subdirectory. Inside it, add two
files:

The first one is the ``package.json`` listing of dependencies, with the
following contents:

.. literalinclude:: code/node-app/src/package.json
    :caption: package.json
    :language: json

The second file is our sample app, a simple "hello world" server. Still inside
``src/``, add the following contents to ``server.js``:

.. literalinclude:: code/node-app/src/server.js
    :caption: server.js
    :language: javascript

Next, we'll setup the Rockcraft project. In the original empty folder, create
an empty file called ``rockcraft.yaml``. Then add the following snippets, one
after the other:

Add the metadata that describes your ROCK, such as its name and licence:

.. literalinclude:: code/node-app/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml
    :start-after: [docs:rock-metadata]
    :end-before: [docs:rock-metadata-end]

Add the container entrypoint, as a `Pebble`_ service:

.. literalinclude:: code/node-app/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml
    :start-after: [docs:pebble-service]
    :end-before: [docs:pebble-service-end]

Finally, add a part that describes how to build the app created in the ``src/``
directory using the ``npm`` plugin:

.. literalinclude:: code/node-app/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml
    :start-after: [docs:app-part]
    :end-before: [docs:app-part-end]


Pack the ROCK with Rockcraft
----------------------------

To build the ROCK, run:

.. literalinclude:: code/node-app/task.yaml
    :language: bash
    :start-after: [docs:build-rock]
    :end-before: [docs:build-rock-end]
    :dedent: 2

At the end of the process, a file named ``my-node-app_0.1_amd64.rock`` should be
present in the current directory.

Run the ROCK in Docker
----------------------

First, import the recently created ROCK into Docker:

.. literalinclude:: code/node-app/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Since the ROCK bundles a web-app, we'll first start serving that app on local
port 8000:

.. literalinclude:: code/node-app/task.yaml
    :language: bash
    :start-after: [docs:run-container]
    :end-before: [docs:run-container-end]
    :dedent: 2

The output will look similar to this, indicating that Pebble started the ``app``
service:

..  code-block:: text

    2023-10-30T12:37:33.654Z [pebble] Started daemon.
    2023-10-30T12:37:33.659Z [pebble] POST /v1/services 3.878846ms 202
    2023-10-30T12:37:33.659Z [pebble] Started default services with change 1.
    2023-10-30T12:37:33.663Z [pebble] Service "app" starting: node server.js
    2023-10-30T12:37:33.864Z [app] Running on http://0.0.0.0:8080

Next, open your web browser and navigate to ``http://localhost:8000``. You
should see a blank page with a "Hello World from inside the ROCK!" message.
Success!

You can now stop the running container by either interrupting it with CTRL+C or
by running the following in another terminal:

.. literalinclude:: code/node-app/task.yaml
    :language: bash
    :start-after: [docs:stop-container]
    :end-before: [docs:stop-container-end]
    :dedent: 2

References
----------

The sample app code comes from the "Hello world example" Express tutorial,
available at https://expressjs.com/en/starter/hello-world.html.


.. _`Pebble`:  https://github.com/canonical/pebble
.. _`NodeSource`: https://nodesource.com/
