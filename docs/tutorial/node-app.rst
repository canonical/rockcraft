.. _bundle_a_nodejs_app_within_a_rock:

Bundle a Node.js app within a rock
**********************************

This tutorial describes the steps needed to bundle a typical Node.js application
into a rock.

Setup your environment
----------------------

.. include:: /reuse/tutorial/setup_stable.rst

Project setup
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
after the other.

Add the metadata that describes your rock, such as its name and licence:

.. literalinclude:: code/node-app/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml
    :start-at: name: my-node-app
    :end-at: amd64:

Add the container entrypoint, as a `Pebble`_ service:

.. literalinclude:: code/node-app/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml
    :start-at: services:
    :end-at: working-dir: /lib/node_modules/node_web_app

Finally, add a part that describes how to build the app created in the ``src/``
directory using the ``npm`` plugin:

.. literalinclude:: code/node-app/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml
    :start-at: parts:
    :end-at: source: src/

The whole file then looks like this:

.. literalinclude:: code/node-app/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml


Pack the rock with Rockcraft
----------------------------

To build the rock, run:

.. literalinclude:: code/node-app/task.yaml
    :language: bash
    :start-after: [docs:build-rock]
    :end-before: [docs:build-rock-end]
    :dedent: 2

At the end of the process, a new rock file should be present in the current
directory:

.. literalinclude:: code/node-app/task.yaml
    :language: bash
    :start-after: [docs:check-rock]
    :end-before: [docs:check-rock-end]
    :dedent: 2

Run the rock
----------------------

.. tabs::

    .. group-tab:: Docker

        First, import the recently created rock into Docker:

        .. literalinclude:: code/node-app/task.yaml
            :language: bash
            :start-after: [docs:skopeo-copy]
            :end-before: [docs:skopeo-copy-end]
            :dedent: 2

        Since the rock bundles a web-app, we'll first start serving that app on local
        port 8000:

        .. literalinclude:: code/node-app/task.yaml
            :language: bash
            :start-after: [docs:run-container]
            :end-before: [docs:run-container-end]
            :dedent: 2

    .. group-tab:: Podman

        Run the oci archive directly, and start serving the app on local port 8000:

        .. literalinclude:: code/node-app/task.yaml
            :language: bash
            :start-after: [docs:podman-run]
            :end-before: [docs:podman-run-end]
            :dedent: 2

The output will look similar to this, indicating that Pebble started the ``app``
service:

..  code-block:: text

    2023-10-30T12:37:33.654Z [pebble] Started daemon.
    2023-10-30T12:37:33.659Z [pebble] POST /v1/services 3.878846ms 202
    2023-10-30T12:37:33.659Z [pebble] Started default services with change 1.
    2023-10-30T12:37:33.663Z [pebble] Service "app" starting: node server.js
    2023-10-30T12:37:33.864Z [app] Running on http://0.0.0.0:8080

Next we'll verify that the Node.js app is up and running. If you're working on
a regular Ubuntu system, open your web browser and go to
``http://localhost:8000``. You should see a blank page with a
"Hello World from inside the rock!" message. Success!

If, instead, you're working in a Multipass VM, you can
open another shell into the VM and access the app with curl:

.. literalinclude:: code/node-app/task.yaml
    :language: bash
    :prepend: multipass shell rock-dev
    :start-after: [docs:curl-localhost]
    :end-before: [docs:curl-localhost-end]
    :dedent: 2

This should also print "Hello World from inside the rock!" to the terminal.

You can now stop the running container by either interrupting it with
:kbd:`Ctrl` + :kbd:`C` or by running the following in another terminal:

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
