Bundle a Node.js app into a ROCK
********************************

This tutorial describes the steps needed to bundle a typical Node.js application
into a ROCK.

Prerequisites
-------------
- snap enabled system (https://snapcraft.io)
- LXD installed (https://linuxcontainers.org/lxd/getting-started-cli/)
- skopeo installed (https://github.com/containers/skopeo)
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
    :language: json

The second file is our sample app, a simple "hello world" server. Still inside
``src/``, add the following contents to ``server.js``:

.. literalinclude:: code/node-app/src/server.js
    :language: javascript

Next, we'll setup the Rockcraft project. In the original empty folder, create
an empty file called ``rockcraft.yaml``. Then add the following snippets, one
after the other:

Add the metadata that describes your ROCK, such as its name and license:

.. literalinclude:: code/node-app/rockcraft.yaml
    :language: yaml
    :start-after: [docs:rock-metadata]
    :end-before: [docs:rock-metadata-end]

Add the container entrypoint, as a `Pebble`_ service:

.. literalinclude:: code/node-app/rockcraft.yaml
    :language: yaml
    :start-after: [docs:pebble-service]
    :end-before: [docs:pebble-service-end]

Add a part declaring the dependency on the ``nodejs`` Ubuntu package:

.. literalinclude:: code/node-app/rockcraft.yaml
    :language: yaml
    :start-after: [docs:node-part]
    :end-before: [docs:node-part-end]

Add another part, describing how to build the app created in the ``src/``
directory:

.. literalinclude:: code/node-app/rockcraft.yaml
    :language: yaml
    :start-after: [docs:app-part]
    :end-before: [docs:app-part-end]

Finally, add the `NodeSource`_ Ubuntu repository so that the ROCK uses a newer
version of Node.js than is available in the official LTS archives:

.. literalinclude:: code/node-app/rockcraft.yaml
    :language: yaml
    :start-after: [docs:nodesource-repo]
    :end-before: [docs:nodesource-repo-end]


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

..  code-block:: bash

  docker run -p8000:8080 --rm -it my-node-app:latest

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

References
----------

The sample app code comes from the "Dockerizing a Node.js web app" tutorial,
available at https://nodejs.org/en/docs/guides/nodejs-docker-webapp.


.. _`Pebble`:  https://github.com/canonical/pebble
.. _`NodeSource`: https://nodesource.com/
