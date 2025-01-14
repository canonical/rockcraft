.. _build-a-rock-for-an-expressjs-application:

Build a rock for an ExpressJS application
-----------------------------------------

In this tutorial, we'll create a simple ExpressJS application and learn how to
containerise it in a rock with Rockcraft's
:ref:`expressjs-framework <expressjs-framework-reference>` extension.

Setup
=====

.. include:: /reuse/tutorial/setup.rst

Before we go any further, for this tutorial we'll need the most recent version
of Rockcraft on the edge channel. Run ``sudo snap refresh rockcraft --channel
latest/edge`` to switch to it.

Finally, create a new directory for this tutorial and go inside it:

.. code-block:: bash

   mkdir expressjs-hello-world
   cd expressjs-hello-world

Create the ExpressJS application
================================

Let's start by creating the "Hello, world" ExpressJS application that we'll use
throughout this tutorial.

Create the ExpressJS application by running the express-generator.


.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:init-app]
    :end-before: [docs:init-app-end]
    :dedent: 2

Run the ExpressJS application using ``npm start`` to verify
that it works.

Test the ExpressJS application by using ``curl`` to send a request to the root
endpoint. We'll need a new terminal for this -- if we're using Multipass, run
``multipass shell rock-dev`` to get another terminal:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:curl-expressjs]
    :end-before: [docs:curl-expressjs-end]
    :dedent: 2

The ExpressJS application should respond with a ``Welcome to Express`` HTML web
page.

The application looks good, so let's stop it for now by pressing :kbd:`Ctrl` +
:kbd:`C`.

Pack the ExpressJS application into a rock
==========================================

First, we'll need a ``rockcraft.yaml`` file. Rockcraft will automate its
creation and tailoring for a ExpressJS application by using the
``expressjs-framework`` profile:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

The ``rockcraft.yaml`` file will automatically be created in the project's
working directory. Open it in a text editor and check that the ``name`` is
``expressjs-hello-world``. Ensure that ``platforms`` includes the architecture
of the host. For example, if the host uses the ARM architecture, include
``arm64`` in ``platforms``.

.. note::
    For this tutorial, we'll use the ``name`` ``expressjs-hello-world`` and
    assume we're running on the  ``amd64`` platform. Check the architecture of
    the system using ``dpkg --print-architecture``.

    The ``name``, ``version`` and ``platform`` all influence the name of the
    generated ``.rock`` file.

Pack the rock:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

.. note::

    Depending on the network, this step can take a couple of minutes to finish.

    ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS`` is required whilst the
    ExpressJS extension is experimental.

Once Rockcraft has finished packing the ExpressJS rock, we'll find a new file in
the project's working directory (an `OCI <OCI_image_spec_>`_ archive) with
the ``.rock`` extension:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2

The created rock is about 92MB in size. We will reduce its size later in this
tutorial.

.. note::
    If we changed the ``name`` or ``version`` in ``rockcraft.yaml`` or are not
    on an ``amd64`` platform, the name of the ``.rock`` file will be
    different.

    The size of the rock may vary depending on factors like the architecture
    we are building on and the packages installed at the time of packing.

Run the ExpressJS rock with Docker
==================================

We already have the rock as an `OCI <OCI_image_spec_>`_ archive. Now we
need to load it into Docker:

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

The output should list the ExpressJS container image, along with its tag, ID and
size:

..  code-block:: text
    :class: log-snippets

    REPOSITORY              TAG       IMAGE ID       CREATED       SIZE
    expressjs-hello-world   0.1       30c7e5aed202   2 weeks ago   193MB

.. note::
    The size of the image reported by Docker is the uncompressed size which is
    larger than the size of the compressed ``.rock`` file.

Now we're finally ready to run the rock and test the containerised ExpressJS
application:

.. literalinclude:: code/expressjs/task.yaml
    :language: text
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use the same ``curl`` command as before to send a request to the ExpressJS
application's root endpoint which is running inside the container:

.. literalinclude:: code/expressjs/task.yaml
    :language: text
    :start-after: [docs:curl-expressjs-rock]
    :end-before: [docs:curl-expressjs-rock-end]
    :dedent: 2

The ExpressJS application should again respond with ``Welcome to Express`` HTML.

View the application logs
~~~~~~~~~~~~~~~~~~~~~~~~~

When deploying the ExpressJS rock, we can always get the application logs via
``pebble``:

.. literalinclude:: code/expressjs/task.yaml
    :language: text
    :start-after: [docs:get-logs]
    :end-before: [docs:get-logs-end]
    :dedent: 2

As a result, :ref:`pebble_explanation_page` will give us the logs for the
``expressjs`` service running inside the container.
We should expect to see something similar to this:

..  code-block:: text
    :class: log-snippets

    app@0.0.0 start
    node ./bin/www
    GET / 200 62.934 ms - 170

We can also choose to follow the logs by using the ``-f`` option with the
``pebble logs`` command above. To stop following the logs, press :kbd:`Ctrl` +
:kbd:`C`.

Cleanup
~~~~~~~

Now we have a fully functional rock for a ExpressJS application! This concludes
the first part of this tutorial, so we'll stop the container and remove the
respective image for now:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2

Chisel the rock
===============

This is an optional but recommended step, especially if we're looking to
deploy the rock into a production environment. With :ref:`chisel_explanation`
we can produce lean and production-ready rocks by getting rid of all the
contents that are not needed for the ExpressJS application to run. This results
in a much smaller rock with a reduced attack surface.

.. note::
    It is recommended to run chiselled images in production. For development,
    we may prefer non-chiselled images as they will include additional
    development tooling (such as for debugging).

The first step towards chiselling the rock is to ensure we are using a
``bare`` :ref:`base <bases_explanation>`.
In ``rockcraft.yaml``, change the ``base`` to ``bare`` and add
``build-base: ubuntu@24.04``:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:change-base]
    :end-before: [docs:change-base-end]
    :dedent: 2

.. note::
    The ``sed`` command replaces the current ``base`` in ``rockcraft.yaml`` with
    the ``bare`` base. Note that ``build-base`` is also required when using the
    ``bare`` base.

So that we can compare the size after chiselling, open the ``rockcraft.yaml``
file and change the ``version`` (e.g. to ``0.1-chiselled``). Pack the rock with
the new ``bare`` :ref:`base <bases_explanation>`:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:chisel-pack]
    :end-before: [docs:chisel-pack-end]
    :dedent: 2

As before, verify that the new rock was created:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:ls-bare-rock]
    :end-before: [docs:ls-bare-rock-end]
    :dedent: 2

We'll verify that the new ExpressJS rock is now approximately **20% smaller**
in size! And that's just because of the simple change of ``base``.

And the functionality is still the same. As before, we can confirm this by
running the rock with Docker

.. literalinclude:: code/expressjs/task.yaml
    :language: text
    :start-after: [docs:docker-run-chisel]
    :end-before: [docs:docker-run-chisel-end]
    :dedent: 2

and then using the same ``curl`` request:

.. literalinclude:: code/expressjs/task.yaml
    :language: text
    :start-after: [docs:curl-expressjs-bare-rock]
    :end-before: [docs:curl-expressjs-bare-rock-end]
    :dedent: 2

Unsurprisingly, the ExpressJS application should still respond with
``Welcome to Express`` HTML.

Cleanup
~~~~~~~

And that's it. We can now stop the container and remove the corresponding
image:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-chisel]
    :end-before: [docs:stop-docker-chisel-end]
    :dedent: 2

.. _update-expressjs-application:

Update the ExpressJS application
================================

As a final step, let's update our application. For example,
we want to add a new ``/time`` endpoint which returns the current time.

Start by opening the ``time.js`` file in a text editor and update the code to
look like the following:

.. literalinclude:: code/expressjs/time.js
    :language: python

Place ``time.js`` file into the appropriate ``routes/`` directory. Import the
time route from the the main ``app.js`` file and update the code to look like
the following:

.. literalinclude:: code/expressjs/app.js
    :language: javascript

Notice the addition of timerouter import and the registration of the ``/time``
endpoint.

Since we are creating a new version of the application, open the
``rockcraft.yaml`` file and change the ``version`` (e.g. to ``0.2``).

.. note::

    ``rockcraft pack`` will create a new image with the updated code even if we
    don't change the version. It is recommended to change the version whenever
    we make changes to the application in the image.

Pack and run the rock using similar commands as before:

.. literalinclude:: code/expressjs/task.yaml
    :language: text
    :start-after: [docs:docker-run-update]
    :end-before: [docs:docker-run-update-end]
    :dedent: 2

.. note::

    Note that the resulting ``.rock`` file will now be named differently, as
    its new version will be part of the filename.

Finally, use ``curl`` to send a request to the ``/time`` endpoint:

.. literalinclude:: code/expressjs/task.yaml
    :language: text
    :start-after: [docs:curl-time]
    :end-before: [docs:curl-time-end]
    :dedent: 2

The updated application should respond with the current date and time (e.g.
``Fri Jan 10 2025 03:11:44 GMT+0000 (Coordinated Universal Time)``).

.. note::

    If you are getting a ``404`` for the ``/time`` endpoint, check the
    :ref:`troubleshooting-expressjs` steps below.

Cleanup
~~~~~~~

We can now stop the container and remove the corresponding image:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-updated]
    :end-before: [docs:stop-docker-updated-end]
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

.. _troubleshooting-expressjs:

Troubleshooting
===============

**Application updates not taking effect?**

Upon changing your ExpressJS application and re-packing the rock, if you believe
your changes are not taking effect (e.g. the ``/time``
:ref:`endpoint <update-expressjs-application>` is returning a
404), try running ``rockcraft clean`` and pack the rock again with
``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/install-multipass
