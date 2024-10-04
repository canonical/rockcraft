.. _build-a-rock-for-a-fastapi-application:

Build a rock for a FastAPI application
--------------------------------------

In this tutorial, we'll create a simple FastAPI application and learn how to
containerise it in a rock, using Rockcraft's ``fastapi-framework``
:ref:`extension <fastapi-framework-reference>`.

Setup
=====

.. include:: /reuse/tutorial/setup.rst

.. note::
    This tutorial requires the ``latest/edge`` channel of Rockcraft. Use
    ``sudo snap refresh rockcraft --channel latest/edge`` to get the latest
    edge version.

Finally, create a new directory for this tutorial and go inside it:

.. code-block:: bash

   mkdir fastapi-hello-world
   cd fastapi-hello-world

Create the FastAPI application
==============================

Start by creating the "Hello, world" FastAPI application that will be used for
this tutorial.

Create a ``requirements.txt`` file, copy the following text into it and then
save it:

.. literalinclude:: code/fastapi/requirements.txt

In order to test the FastAPI application locally (before packing it into a
rock), install ``python3-venv`` and create a virtual environment:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:create-venv]
    :end-before: [docs:create-venv-end]
    :dedent: 2

In the same directory, copy and save the following into a text file called
``app.py``:

.. literalinclude:: code/fastapi/app.py
    :language: python

Run the FastAPI application using ``fastapi dev app.py --port 8000`` to verify
that it works.

Test the FastAPI application by using ``curl`` to send a request to the root
endpoint. You may need a new terminal for this, if you are using Multipass use
``multipass shell rock-dev`` to get another terminal:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:curl-fastapi]
    :end-before: [docs:curl-fastapi-end]
    :dedent: 2

The FastAPI application should respond with ``{"message":"Hello World"}``.

The Django application looks good, so let's stop it for now by pressing
:kbd:`Ctrl` + :kbd:`C`.

Pack the FastAPI application into a rock
========================================

First, we'll need a ``rockcraft.yaml`` file. Rockcraft will automate its
creation and tailoring for a FastAPI application by using the
``fastapi-framework`` profile:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

The ``rockcraft.yaml`` file will automatically be created in your working
directory. Open it in a text editor and check that the ``name`` is
``fastapi-hello-world``. Ensure that ``platforms`` includes the architecture of
your host. For example, if your host uses the ARM
architecture, include ``arm64`` in ``platforms``.

.. note::
    For this tutorial, we'll use the ``name`` ``fastapi-hello-world`` and assume
    you are running on an ``amd64`` platform. Check the architecture of your
    system using ``dpkg --print-architecture``.

    The ``name``, ``version`` and ``platform`` all influence the name of the
    generated ``.rock`` file.

Pack the rock:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

.. note::

    Depending on your network, this step can take a couple of minutes to finish.

    ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS`` is required whilst the FastAPI
    extension is experimental.

Once Rockcraft has finished packing the FastAPI rock, you'll find a new file in
your working directory (an `OCI <OCI_image_spec_>`_ archive) with the ``.rock``
extension:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2

The created rock is about 75MB in size. We will reduce its size later in this
tutorial.

.. note::
    If you changed the ``name`` or ``version`` in ``rockcraft.yaml`` or are not
    on an ``amd64`` platform, the name of the ``.rock`` file will be different
    for you.

    The size of your rock may vary depending on factors like the architecture
    you are building on and the packages installed at the time of packing.

Run the FastAPI rock with Docker
================================

We already have the rock as an `OCI <OCI_image_spec_>`_ archive. Now we
need to load it into Docker:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Check that the image was successfully loaded into Docker:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:docker-images]
    :end-before: [docs:docker-images-end]
    :dedent: 2

The output should list the FastAPI container image, along with its tag, ID and
size:

..  code-block:: text
    :class: log-snippets

    REPOSITORY            TAG       IMAGE ID       CREATED       SIZE
    fastapi-hello-world   0.1       30c7e5aed202   2 weeks ago   193MB

.. note::
    The size of the image reported by Docker is the uncompressed size which is
    larger than the size of the compressed ``.rock`` file.

Now we're finally ready to run the rock and test your containerised FastAPI
application:

.. literalinclude:: code/fastapi/task.yaml
    :language: text
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use the same ``curl`` command as before to send a request to the FastAPI
application's root endpoint which is running inside the container:

.. literalinclude:: code/fastapi/task.yaml
    :language: text
    :start-after: [docs:curl-fastapi-rock]
    :end-before: [docs:curl-fastapi-rock-end]
    :dedent: 2

The FastAPI application should again respond with ``{"message":"Hello World"}``.

View the application logs
~~~~~~~~~~~~~~~~~~~~~~~~~

When deploying the FastAPI rock, you can always get the application logs via
``pebble``:

.. literalinclude:: code/fastapi/task.yaml
    :language: text
    :start-after: [docs:get-logs]
    :end-before: [docs:get-logs-end]
    :dedent: 2

As a result, :ref:`pebble_explanation_page` will give you the logs for the
``fastapi`` service running inside the container.
You should expect to see something similar to this:

..  code-block:: text
    :class: log-snippets

    2024-10-01T06:32:50.180Z [fastapi] INFO:     Started server process [12]
    2024-10-01T06:32:50.181Z [fastapi] INFO:     Waiting for application startup.
    2024-10-01T06:32:50.181Z [fastapi] INFO:     Application startup complete.
    2024-10-01T06:32:50.182Z [fastapi] INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    2024-10-01T06:32:58.214Z [fastapi] INFO:     172.17.0.1:55232 - "GET / HTTP/1.1" 200 OK

You can also choose to follow the logs by using the ``-f`` option with the
``pebble logs`` command above. To stop following the logs, press :kbd:`Ctrl` +
:kbd:`C`.

Cleanup
~~~~~~~

Now we have a fully functional rock for a FastAPI application! This concludes
the first part of this tutorial, so we'll stop the container and remove the
respective image for now:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2

Chisel the rock
===============

This is an optional but recommended step, especially if you're looking to
deploy your rock into a production environment. With :ref:`chisel_explanation`
you can produce lean and production-ready rocks by getting rid of all the
contents that are not needed for your FastAPI application to run. This results
in a much smaller rock with a reduced attack surface.

.. note::
    It is recommended to run chiselled images in production. For development,
    you may prefer non-chiselled images as they will include additional
    development tooling (such as for debugging).

The first step towards chiselling the rock is to ensure we are using a
``bare`` :ref:`base <bases_explanation>`.
In ``rockcraft.yaml``, change the ``base`` to ``bare`` and add
``build-base: ubuntu@24.04``:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:change-base]
    :end-before: [docs:change-base-end]
    :dedent: 2

.. note::
    The ``sed`` command replaces the current ``base`` in ``rockcraft.yaml`` with
    the ``bare`` base. The command also adds a ``build-base`` which is required
    when using the ``bare`` base.

So that we can compare the size after chiselling, **open the**
``rockcraft.yaml`` file and change the ``version`` (e.g. to ``0.1-chiselled``).
Pack the rock with the new ``bare`` :ref:`base <bases_explanation>`:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:chisel-pack]
    :end-before: [docs:chisel-pack-end]
    :dedent: 2

As before, verify that the new rock was created:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:ls-bare-rock]
    :end-before: [docs:ls-bare-rock-end]
    :dedent: 2

You'll verify that the new FastAPI rock is now approximately **35% smaller**
in size! And that's just because of the simple change of ``base``.

And the functionality is still the same. As before, we can confirm this by
running the rock with Docker

.. literalinclude:: code/fastapi/task.yaml
    :language: text
    :start-after: [docs:docker-run-chisel]
    :end-before: [docs:docker-run-chisel-end]
    :dedent: 2

and then using the same ``curl`` request:

.. literalinclude:: code/fastapi/task.yaml
    :language: text
    :start-after: [docs:curl-fastapi-bare-rock]
    :end-before: [docs:curl-fastapi-bare-rock-end]
    :dedent: 2

Unsurprisingly, the FastAPI application should still respond with
``{"message":"Hello World"}``.

Cleanup
~~~~~~~

And that's it. We can now stop the container and remove the corresponding
image:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-chisel]
    :end-before: [docs:stop-docker-chisel-end]
    :dedent: 2

.. _update-fastapi-application:

Update FastAPI application
==========================

As a final step, let's update our application. For example,
we want to add a new ``/time`` endpoint which returns the current time.

Start by opening the ``app.py`` file in a text editor and update the code to
look like the following:

.. literalinclude:: code/fastapi/time_app.py
    :language: python

Since we are creating a new version of the application, **open the**
``rockcraft.yaml`` file and change the ``version`` (e.g. to ``0.2``).

.. note::

    ``rockcraft pack`` will create a new image with the updated code even if you
    don't change the version. It is recommended to change the version whenever
    you make changes to the application in the image.

Pack and run the rock using similar commands as before:

.. literalinclude:: code/fastapi/task.yaml
    :language: text
    :start-after: [docs:docker-run-update]
    :end-before: [docs:docker-run-update-end]
    :dedent: 2

.. note::

    Note that the resulting ``.rock`` file will now be named differently, as
    its new version will be part of the filename.

Finally, use ``curl`` to send a request to the ``/time`` endpoint:

.. literalinclude:: code/fastapi/task.yaml
    :language: text
    :start-after: [docs:curl-time]
    :end-before: [docs:curl-time-end]
    :dedent: 2

The updated application should respond with the current date and time (e.g.
``{"value":"2024-10-01 06:53:54\n"}``).

.. note::

    If you are getting a ``404`` for the ``/time`` endpoint, check the
    :ref:`troubleshooting-fastapi` steps below.

Cleanup
~~~~~~~

We can now stop the container and remove the corresponding image:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-updated]
    :end-before: [docs:stop-docker-updated-end]
    :dedent: 2

Reset your environment
======================

We've reached the end of this tutorial.

If you'd like to reset your working environment, you can simply run the
following:

.. literalinclude:: code/fastapi/task.yaml
    :language: bash
    :start-after: [docs:cleanup]
    :end-before: [docs:cleanup-end]
    :dedent: 2

.. collapse:: If using Multipass...

    If you created an instance using Multipass, you can also clean it up.
    Start by exiting it:

    .. code-block:: bash

        exit

    And then you can proceed with its deletion:

    .. code-block:: bash

        multipass delete rock-dev
        multipass purge

----

.. _troubleshooting-fastapi:

Troubleshooting
===============

**Application updates not taking effect?**

Upon changing your FastAPI application and re-packing the rock, if you believe
your changes are not taking effect (e.g. the ``/time``
:ref:`endpoint <update-fastapi-application>` is returning a
404), try running ``rockcraft clean`` and pack the rock again with
``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/how-to-install-multipass
