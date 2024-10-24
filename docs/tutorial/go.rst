.. _build-a-rock-for-a-go-application:

Build a rock for a Go application
------------------------------------

In this tutorial, we'll create a simple Go application and learn how to
containerise it in a rock, using Rockcraft's ``go-framework``
:ref:`extension <go-framework-reference>`.

Setup
=====

.. include:: /reuse/tutorial/setup.rst

.. note::
    This tutorial requires the ``latest/edge`` channel of Rockcraft. Use
    ``sudo snap refresh rockcraft --channel latest/edge`` to get the latest
    edge version.

Finally, create a new directory for this tutorial and go inside it:

.. code-block:: bash

   mkdir go-hello-world
   cd go-hello-world

Create the Go application
==============================

Start by creating the "Hello, world" Go application that will be used for
this tutorial.

In order to test the Go application locally (before packing it into a rock),
install ``go``.

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:install-go]
    :end-before: [docs:install-go-end]
    :dedent: 2

Initialise the new Go module:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:mod-init-go]
    :end-before: [docs:mod-init-go-end]
    :dedent: 2

Create a ``main.go`` file, copy the following text into it and then
save it:

.. literalinclude:: code/go/main.go
    :language: go

Build the Go application so it can be run:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:go-build]
    :end-before: [docs:go-build-end]
    :dedent: 2

A new binary named ``go-hello-world`` should be in the current
directory.  This binary is only needed for local testing, as
Rockcraft will compile the Go application. Run the Go application using
``./go-hello-world`` to verify that it works.

Test the Go application by using ``curl`` to send a request to the root
endpoint. We may need a new terminal for this, if we are using Multipass use
``multipass shell rock-dev`` to get another terminal:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:curl-go]
    :end-before: [docs:curl-go-end]
    :dedent: 2

The Go application should respond with ``Hello, world!``.

The Go application looks good, so stop it for now using :kbd:`Ctrl` + :kbd:`C`.

Pack the Go application into a rock
===================================


First, we'll need a ``rockcraft.yaml`` file. Rockcraft will automate its
creation and tailor it for a Go application by using the
``go-framework`` profile:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

The ``rockcraft.yaml`` file will automatically be created in the project working
directory. Open it in a text editor and check that the ``name`` is
``go-hello-world``. Ensure that ``platforms`` includes the architecture of
the host. For example, if the host uses the ARM
architecture, include ``arm64`` in ``platforms``.

.. note::
    For this tutorial, we'll use the ``name`` ``go-hello-world`` and assume
    we are running on an ``amd64`` platform. Check the architecture of the
    system using ``dpkg --print-architecture``.

    The ``name``, ``version`` and ``platform`` all influence the name of the
    generated ``.rock`` file.

Pack the rock:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

.. note::

    Depending on the network, this step can take a couple of minutes to finish.

    ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS`` is required whilst the ``go-framework``
    extension is experimental.

Once Rockcraft has finished packing the Go rock, we'll find a new file in
the working directory (an `OCI <OCI_image_spec_>`_ archive) with the ``.rock``
extension:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2

.. note::
    If we changed the ``name`` or ``version`` in ``rockcraft.yaml`` or are not
    on an ``amd64`` platform, the name of the ``.rock`` file will be different.

    By default, the ``go-framework`` will use the ``bare`` base.
    The ``bare`` base is recommended for production applications because
    the image size will be smaller, and the risk of security issues lower.
    However, we may want to change the base to ``ubuntu@24.04`` during the
    development process to benefit from the extra utilities provided.


Run the Go rock with Docker
===========================


We already have the rock as an `OCI <OCI_image_spec_>`_ archive. Load the
image into Docker:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2


Check that the image was successfully loaded into Docker:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:docker-images]
    :end-before: [docs:docker-images-end]
    :dedent: 2

The output should list the Go container image, along with its tag, ID and
size:

..  code-block:: text
    :class: log-snippets

    REPOSITORY       TAG       IMAGE ID       CREATED         SIZE
    go-hello-world   0.1       f3abf7ebc169   5 minutes ago   15.7MB

.. note::
    The size of the image reported by Docker is the uncompressed size which is
    larger than the size of the compressed ``.rock`` file.

Now we're finally ready to run the rock and test the containerised Go
application:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use the same ``curl`` command as before to send a request to the Go
application's root endpoint which is running inside the container:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:curl-go-rock]
    :end-before: [docs:curl-go-rock-end]
    :dedent: 2

The Go application should again respond with ``Hello, world!``.


View the application logs
~~~~~~~~~~~~~~~~~~~~~~~~~

When deploying the Go rock, we can always get the application logs via
:ref:`pebble_explanation_page`:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:get-logs]
    :end-before: [docs:get-logs-end]
    :dedent: 2

As a result, ``pebble`` will give the logs for the
``go`` service running inside the container.
We should expect to see something similar to this:

..  code-block:: text
    :class: log-snippets

    2024-10-04T08:51:35.826Z [go] 2024/10/04 08:51:35 starting hello world application
    2024-10-04T08:51:39.974Z [go] 2024/10/04 08:51:39 new hello world request

We can also choose to follow the logs by using the ``-f`` option with the
``pebble logs`` command above. To stop following the logs, press :kbd:`Ctrl` + :kbd:`C`.


Stop the application
~~~~~~~~~~~~~~~~~~~~

Now we have a fully functional rock for a Go application! This concludes
the first part of this tutorial, so we'll stop the container and remove the
respective image for now:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2


Update Go application
========================================

As a final step, let's update our application. For example,
we want to add a new ``/time`` endpoint which returns the current time.

Start by opening the ``main.go`` file in a text editor and update the code to
look like the following:

.. literalinclude:: code/go/main.go.time
    :language: go

Since we are creating a new version of the application, open the
``rockcraft.yaml`` file and change the ``version`` (e.g. to ``0.2``).

.. note::

    ``rockcraft pack`` will create a new image with the updated code even if we
    don't change the version. It is recommended to change the version whenever
    we make changes to the application in the image.

Pack and run the rock using similar commands as before:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:docker-run-update]
    :end-before: [docs:docker-run-update-end]
    :dedent: 2

.. note::

    Note that the resulting ``.rock`` file will now be named differently, as
    its new version will be part of the filename.

Finally, use ``curl`` to send a request to the ``/time`` endpoint:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:curl-time]
    :end-before: [docs:curl-time-end]
    :dedent: 2

The updated application should respond with the current date and time (e.g.
``2024-06-21 09:47:56``).

.. note::

    If we are not getting the current date and time from the ``/time``
    endpoint, check the :ref:`troubleshooting-go` steps below.


Cleanup
~~~~~~~

We can now stop the container and remove the corresponding image:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-updated]
    :end-before: [docs:stop-docker-updated-end]
    :dedent: 2


Reset the environment
======================

We've reached the end of this tutorial.

If we'd like to reset the working environment, we can simply run the
following:

.. literalinclude:: code/go/task.yaml
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
* :ref:`go-framework reference<go-framework-reference>`.
* :ref:`why_use_rockcraft`.
* :ref:`What is a Rock?<rocks_explanation>`.

----

.. _troubleshooting-go:

Troubleshooting
===============

**Application updates not taking effect?**

Upon changing the Go application and re-packing the rock, if
the changes are not taking effect, try running ``rockcraft clean`` and pack
the rock again with ``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/install-multipass
