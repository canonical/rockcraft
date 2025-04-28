.. _build-a-rock-for-an-expressjs-application:

Build a rock for an ExpressJS application
-----------------------------------------

In this tutorial, we'll containerise a simple ExpressJS application into a rock
using Rockcraft's ``expressjs-framework`` :ref:`extension
<expressjs-framework-reference>`.

It should take 25 minutes for you to complete.

You won’t need to come prepared with intricate knowledge of software
packaging, but familiarity with Linux paradigms, terminal operations,
and ExpressJS is required.

Once you complete this tutorial, you’ll have a working rock for an ExpressJS
application. You’ll gain familiarity with Rockcraft and the
``expressjs-framework`` extension, and have the experience to create
rocks for ExpressJS applications.

Setup
=====

.. include:: /reuse/tutorial/setup_edge.rst

This tutorial requires the ``latest/edge`` channel of Rockcraft. Run
``sudo snap refresh rockcraft --channel latest/edge`` to get the latest
edge version.

In order to test the ExpressJS application locally, before packing it into a
rock, install ``npm`` and initialize the starter app.

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:install-deps]
    :end-before: [docs:install-deps-end]
    :dedent: 2


Create the ExpressJS application
================================

Start by generating the ExpressJS starter template using the express-generator.

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:init-app]
    :end-before: [docs:init-app-end]
    :dedent: 2

Let's Run the Express application to verify that it works:

.. code:: bash

  npm start

The application starts an HTTP server listening on port 3000
that we can test by using curl to send a request to the root
endpoint. We may need a new terminal for this -- if using Multipass, run
``multipass shell rock-dev`` to get another terminal:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:curl-expressjs]
    :end-before: [docs:curl-expressjs-end]
    :dedent: 2

The ExpressJS application should respond with *Welcome to Express* web page.

.. note::
    The response from the ExpressJS application includes HTML and CSS which
    makes it difficult to read on a terminal. Visit ``http://localhost:3000``
    using a browser to see the fully rendered page.

The ExpressJS application looks good, so let's stop it for now
with :kbd:`Ctrl` + :kbd:`C`, then move out of the application directory
``cd ..``.

Pack the Express application into a rock
========================================

First, we'll need a ``rockcraft.yaml`` project file. Rockcraft will automate its
creation and tailor it for a ExpressJS application when we tell it to use the
``expressjs-framework`` profile:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

Open ``rockcraft.yaml`` in a text editor and check that the ``name``
key is set to ``expressjs-hello-world``. Ensure that ``platforms`` includes
the architecture of the host. For example, if the host uses the ARM
architecture, include ``arm64`` in ``platforms``.

As the ``expressjs-framework`` extension is still experimental, export the
environment variable ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS``:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:experimental]
    :end-before: [docs:experimental-end]
    :dedent: 2

Pack the rock:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

Depending on the network, this step can take a couple of minutes to finish.

Once Rockcraft has finished packing the ExpressJS rock, we'll find a new file in
the working directory (an `OCI <OCI_image_spec_>`_ image) with the ``.rock``
extension:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2


Run the ExpressJS rock
======================

We already have the rock as an OCI image.

.. tabs::

    .. group-tab:: Docker

        Load the image into Docker:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:skopeo-copy]
            :end-before: [docs:skopeo-copy-end]
            :dedent: 2


        Check that the image was successfully loaded into Docker:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:docker-images]
            :end-before: [docs:docker-images-end]
            :dedent: 2

        The output should list the ExpressJS image, along with its tag, ID and
        size:

        .. terminal::

            REPOSITORY              TAG       IMAGE ID       CREATED       SIZE
            expressjs-hello-world   0.1       30c7e5aed202   2 weeks ago   304MB

        Now we're finally ready to run the rock and test the containerised ExpressJS
        application:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:docker-run]
            :end-before: [docs:docker-run-end]
            :dedent: 2

    .. group-tab:: Podman

        Using podman, run the OCI archive directly:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:podman-run]
            :end-before: [docs:podman-run-end]
            :dedent: 2


Use the same curl command as before to send a request to the ExpressJS
application's root endpoint which is running inside the container:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:curl-expressjs-rock]
    :end-before: [docs:curl-expressjs-rock-end]
    :dedent: 2

The ExpressJS application again responds with *Welcome to Express* page.

View the application logs
~~~~~~~~~~~~~~~~~~~~~~~~~

When deploying the ExpressJS rock, we can always get the application logs with
:ref:`pebble_explanation_page`:

.. tabs::

    .. group-tab:: Docker

        With Docker:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:get-logs]
            :end-before: [docs:get-logs-end]
            :dedent: 2

    .. group-tab:: Podman

        With Podman:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:get-logs-podman]
            :end-before: [docs:get-logs-podman-end]
            :dedent: 2

As a result, Pebble will give us the logs for the
``expressjs`` service running inside the container.
We should expect to see something similar to this:

.. terminal::

    app@0.0.0 start
    node ./bin/www
    GET / 200 62.934 ms - 170

We can also choose to follow the logs by using the ``-f`` option with the
``pebble logs`` command above. To stop following the logs, press :kbd:`Ctrl` +
:kbd:`C`.


Stop the application
~~~~~~~~~~~~~~~~~~~~

Now we have a fully functional rock for a ExpressJS application! This concludes
the first part of this tutorial, so we'll stop the container and remove the
respective image for now:

.. tabs::

    .. group-tab:: Docker

        With Docker:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:stop-docker]
            :end-before: [docs:stop-docker-end]
            :dedent: 2

    .. group-tab:: Podman

        With Podman:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:stop-podman]
            :end-before: [docs:stop-podman-end]
            :dedent: 2


Update the ExpressJS application
================================

For our final task, let's update our application. As an example,
let's add a new ``/time`` endpoint that returns the current time.

Start by creating the ``app/routes/time.js`` file in a text editor and paste the
code from the snippet below:

.. literalinclude:: code/expressjs/time.js
    :caption: time.js
    :language: javascript

Place the code snippet below in ``app/app.js`` under routes registration section
along with other ``app.use(...)`` lines.
It will register the new ``/time`` endpoint:

.. literalinclude:: code/expressjs/time_app.js
    :caption: app.js
    :language: javascript
    :start-after: [docs:append-lines]
    :end-before: [docs:append-lines-end]

Since we are creating a new version of the application, set
``version: '0.2'`` in the project file.

Pack and run the rock using similar commands as before:


.. tabs::

    .. group-tab:: Docker

        With Docker:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:docker-run-update]
            :end-before: [docs:docker-run-update-end]
            :dedent: 2

    .. group-tab:: Podman

        With Podman:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:podman-run-update]
            :end-before: [docs:podman-run-update-end]
            :dedent: 2

The resulting ``.rock`` file will be named differently, as
its new version will be part of the filename.

Finally, use curl to send a request to the ``/time`` endpoint:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:curl-time]
    :end-before: [docs:curl-time-end]
    :dedent: 2

The updated application should respond with the current date and time (e.g.
``Fri Jan 10 2025 03:11:44 GMT+0000 (Coordinated Universal Time)``).

.. tip::

    If you are getting a ``404`` for the ``/time`` endpoint, check the
    :ref:`troubleshooting-expressjs` steps below.

Final Cleanup
~~~~~~~~~~~~~

We can now stop the container and remove the corresponding image:

.. tabs::

    .. group-tab:: Docker

        With Docker:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:stop-docker-updated]
            :end-before: [docs:stop-docker-updated-end]
            :dedent: 2

    .. group-tab:: Podman

        With Podman:

        .. literalinclude:: code/expressjs/task.yaml
            :language: bash
            :start-after: [docs:stop-podman-updated]
            :end-before: [docs:stop-podman-updated-end]
            :dedent: 2

Reset the environment
=====================

We've reached the end of this tutorial.

If we'd like to reset the working environment, we can simply run the
following:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:cleanup]
    :end-before: [docs:cleanup-end]
    :dedent: 2

.. collapse:: If using Multipass...

    If we created an instance using Multipass, we can also clean it up.
    Start by exiting it:

    .. code-block:: bash

        exit

    And then we can proceed with its deletion:

    .. code-block:: bash

        multipass delete rock-dev
        multipass purge

----

Next steps
==========

* :ref:`Rockcraft tutorials<tutorial>`.
* :ref:`expressjs-framework reference<expressjs-framework-reference>`.
* :ref:`why_use_rockcraft`.
* :ref:`What is a Rock?<rocks_explanation>`.

----

.. _troubleshooting-expressjs:

Troubleshooting
===============

**Application updates not taking effect?**

Upon changing the ExpressJS application and re-packing the rock, if
the changes are not taking effect, try running ``rockcraft clean`` and pack
the rock again with ``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/install-multipass
