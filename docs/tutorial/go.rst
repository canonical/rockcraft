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

Create a ``main.go`` file, copy the following text into it and then
save it:

.. literalinclude:: code/go/main.go
    :language: go

Initialise the new go module:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:mod-init-go]
    :end-before: [docs:mod-init-go-end]
    :dedent: 2


Build the Go application so it can be run:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:go-build]
    :end-before: [docs:go-build-end]
    :dedent: 2

A new binary named ``go-hello-world`` should be in the current directory.
Run the Go application using ``./go-hello-world`` to verify that
it works.

Test the Go application by using ``curl`` to send a request to the root
endpoint. You may need a new terminal for this, if you are using Multipass use
``multipass shell rock-dev`` to get another terminal:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:curl-go]
    :end-before: [docs:curl-go-end]
    :dedent: 2

The Go application should respond with ``Hello World``.

The Go application looks good, so stop it for now using :kbd:`Ctrl` + :kbd:`C`.

Pack the Go application into a rock
===================================


First, we'll need a ``rockcraft.yaml`` file. Rockcraft will automate its
creation and tailoring for a Go application by using the
``go`` profile:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

The ``rockcraft.yaml`` file will automatically be created in your working
directory. Open it in a text editor and check that the ``name`` is
``go-hello-world``. Ensure that ``platforms`` includes the architecture of
your host. For example, if your host uses the ARM
architecture, include ``arm64`` in ``platforms``.

.. note::
    For this tutorial, we'll use the ``name`` ``go-hello-world`` and assume
    you are running on an ``amd64`` platform. Check the architecture of your
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

    Depending on your network, this step can take a couple of minutes to finish.

    ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS`` is required whilst the Go
    extension is experimental.

Once Rockcraft has finished packing the Go rock, you'll find a new file in
your working directory (an `OCI <OCI_image_spec_>`_ archive) with the ``.rock``
extension:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2

.. note::
    If you changed the ``name`` or ``version`` in ``rockcraft.yaml`` or are not
    on an ``amd64`` platform, the name of the ``.rock`` file will be different
    for you.

    By default, the ``go-framework`` will use the ``bare`` base. You can improve
    the developer experience changing the base to ``ubuntu@24.04``, but the
    image size will increase.


Run the Go rock with Docker
===========================


We already have the rock as an `OCI <OCI_image_spec_>`_ archive. Now we
need to load it into Docker:

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

Now we're finally ready to run the rock and test your containerised Go
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

When deploying the Go rock, you can always get the application logs via
``pebble``:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:get-logs]
    :end-before: [docs:get-logs-end]
    :dedent: 2

As a result, :ref:`pebble_explanation_page` will give you the logs for the
``go`` service running inside the container.
You should expect to see something similar to this:

..  code-block:: text
    :class: log-snippets

    2024-10-04T08:51:35.826Z [go] 2024/10/04 08:51:35 starting hello world application
    2024-10-04T08:51:39.974Z [go] 2024/10/04 08:51:39 new hello world request

You can also choose to follow the logs by using the ``-f`` option with the
``pebble logs`` command above. To stop following the logs, press :kbd:`Ctrl` + :kbd:`C`.


Cleanup
~~~~~~~

Now we have a fully functional rock for a Go application! This concludes
the first part of this tutorial, so we'll stop the container and remove the
respective image for now:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2


Add another binary to the Go application
========================================

As a final step, let's update our application to include another binary.

Create a new ``main.go`` file in the directory  ``cmd/anotherserver`` relative
to the base directory of the project, with the following text and then
save it:

.. literalinclude:: code/go/cmd/anotherserver/main.go
    :language: go

Add the following snippet to the file ``rockcraft.yaml``, so the new binary is
set as the main application to run:

.. literalinclude:: code/go/anotherserver_part
    :language: yaml

Since we are creating a new version of the application, **open the**
``rockcraft.yaml`` file and change the ``version`` (e.g. to ``0.2``).

.. note::

    ``rockcraft pack`` will create a new image with the updated code even if you
    don't change the version. It is recommended to change the version whenever
    you make changes to the application in the image.

Pack and run the rock using similar commands as before:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:docker-run-update]
    :end-before: [docs:docker-run-update-end]
    :dedent: 2


.. note::

    Note that the resulting ``.rock`` file will now be named differently, as
    its new version will be part of the filename.

Finally, use ``curl`` to send a request that will be handled by the new
binary in ``anotherserver``:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:curl-anotherserver]
    :end-before: [docs:curl-anotherserver-end]
    :dedent: 2


The Go application should respond with ``Hello, world! (from anotherserver)``.


.. note::

    If you are getting a wrong response, check the
    :ref:`troubleshooting-go` steps below.


Cleanup
~~~~~~~

We can now stop the container and remove the corresponding image:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-updated]
    :end-before: [docs:stop-docker-updated-end]
    :dedent: 2


Reset your environment
======================

We've reached the end of this tutorial.

If you'd like to reset your working environment, you can simply run the
following:

.. literalinclude:: code/go/task.yaml
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

.. _troubleshooting-go:

Troubleshooting
===============

**Application updates not taking effect?**

Upon changing your Go application and re-packing the rock, if you believe
your changes are not taking effect, try running ``rockcraft clean`` and pack
the rock again with ``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/how-to-install-multipass
