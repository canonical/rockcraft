.. _build-a-rock-for-a-go-application:

Build a rock for a Go app
-------------------------

In this tutorial, we'll containerise a simple Go app into a rock using
Rockcraft's ``go-framework`` :ref:`extension <go-framework-reference>`.

It should take 25 minutes for you to complete.

You won’t need to come prepared with intricate knowledge of software
packaging, but familiarity with Linux paradigms, terminal operations,
and Go is required.

Once you complete this tutorial, you’ll have a working rock for a
Go app. You’ll gain familiarity with Rockcraft and the
``go-framework`` extension, and have the experience to create
rocks for Go apps.

Setup
=====

.. include:: /reuse/tutorial/setup_edge.rst

In order to test the Go app locally, before packing it into a rock,
install Go.

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:install-go]
    :end-before: [docs:install-go-end]
    :dedent: 2


Create the Go app
=================

Start by creating the "Hello, world" Go app that will be used for
this tutorial.

Create an empty project directory:

.. code-block:: bash

   mkdir go-hello-world
   cd go-hello-world

Initialise the new Go module:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:mod-init-go]
    :end-before: [docs:mod-init-go-end]
    :dedent: 2

Create a ``main.go`` file, copy the following text into it and then
save it:

.. literalinclude:: code/go/main.go
    :caption: ~/go-hello-world/main.go
    :language: go

Build the Go app so it can be run:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:go-build]
    :end-before: [docs:go-build-end]
    :dedent: 2

A binary called ``go-hello-world`` is created in the current
directory. This binary is only needed for local testing, as
Rockcraft will compile the Go app when we pack the rock.

Let's Run the Go app to verify that it works:

.. code:: bash

  ./go-hello-world

The app starts an HTTP server listening on port 8000
that we can test by using ``curl`` to send a request to the root
endpoint. We may need a new terminal for this -- run
``multipass shell rock-dev`` to get another terminal:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:curl-go]
    :end-before: [docs:curl-go-end]
    :dedent: 2

The Go app should respond with ``Hello, world!``.

The Go app looks good, so let's stop it for now
with :kbd:`Ctrl` + :kbd:`C`.

Pack the Go app into a rock
===========================

Now let's create a container image for our Go app. We'll use a rock,
which is an OCI-compliant container image based on Ubuntu.

First, we'll need a ``rockcraft.yaml`` project file. We'll take advantage of a
pre-defined extension in Rockcraft with the ``--profile`` flag that caters
initial rock files for specific web app frameworks. Using the
Go profile, Rockcraft automates the creation of
``rockcraft.yaml`` and tailors the file for a Go app.
From the ``~/go-hello-world`` directory, initialize the rock:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

The ``rockcraft.yaml`` file will automatically be created and set the name
based on your working directory.

Check out the contents of ``rockcraft.yaml``:

.. code-block:: bash

    cat rockcraft.yaml

The top of the file should look similar to the following snippet:

.. code-block:: yaml
    :caption: ~/go-hello-world/rockcraft.yaml

    name: go-hello-world
    # see https://documentation.ubuntu.com/rockcraft/en/latest/explanation/bases/
    # for more information about bases and using 'bare' bases for chiselled rocks
    base: bare # as an alternative, a ubuntu base can be used
    build-base: ubuntu@24.04 # build-base is required when the base is bare
    version: '0.1' # just for humans. Semantic versioning is recommended
    summary: A summary of your Go app # 79 char long summary
    description: |
        This is go-hello-world's description. You have a paragraph or two to tell the
        most important story about it. Keep it under 100 words though,
        we live in tweetspace and your description wants to look good in the
        container registries out there.
    # the platforms this rock should be built on and run on.
    # you can check your architecture with `dpkg --print-architecture`
    platforms:
        amd64:
        # arm64:
        # ppc64el:
        # s390x:

Verfiy that the ``name`` is ``go-hello-world``.

The ``platforms`` key must match the architecture of your host. Check
the architecture of your system:

.. code-block:: bash

    dpkg --print-architecture


Edit the ``platforms`` key in ``rockcraft.yaml`` if required.

.. note::
    For this tutorial, we name the rock ``go-hello-world`` and assume
    we are running on an ``amd64`` platform. Check the architecture of the
    system using ``dpkg --print-architecture``.

    The ``name``, ``version`` and ``platform`` all influence the name of the
    generated ``.rock`` file.


As the ``go-framework`` extension is still experimental, export the
environment variable ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS``:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:experimental]
    :end-before: [docs:experimental-end]
    :dedent: 2

Pack the rock:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

.. warning::
   There is a `known connectivity issue with LXD and Docker
   <lxd-docker-connectivity-issue_>`_. If we see a
   networking issue such as "*A network related operation failed in a context
   of no network access*" or ``Client.Timeout``, allow egress network traffic
   to flow from the LXD managed bridge using:

   .. code-block::

       iptables  -I DOCKER-USER -i <network_bridge> -j ACCEPT
       ip6tables -I DOCKER-USER -i <network_bridge> -j ACCEPT
       iptables  -I DOCKER-USER -o <network_bridge> -m conntrack \
         --ctstate RELATED,ESTABLISHED -j ACCEPT
       ip6tables -I DOCKER-USER -o <network_bridge> -m conntrack \
         --ctstate RELATED,ESTABLISHED -j ACCEPT

   Run ``lxc network list`` to show the existing LXD managed bridges.

Depending on the network, this step can take a couple of minutes to finish.

Once Rockcraft has finished packing the Go rock, we'll find a new file in
the working directory (an `OCI <OCI_image_spec_>`_ image) with the ``.rock``
extension:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2


Run the Go rock with Docker
===========================


We already have the rock as an `OCI <OCI_image_spec_>`_ archive. Now we
need to load it into Docker. Docker requires rocks to be imported into the
daemon since they can't be run directly like an executable.

Copy the rock:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

This command contains the following pieces:

- ``--insecure-policy``: adopts a permissive policy that
  removes the need for a dedicated policy file.
- ``oci-archive``: specifies the rock we created for our Go app.
- ``docker-daemon``: specifies the name of the image in the Docker registry.

Check that the image was successfully loaded into Docker:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:docker-images]
    :end-before: [docs:docker-images-end]
    :dedent: 2

The output should list the Go container image, along with its tag, ID and
size:

.. terminal::

    REPOSITORY       TAG       IMAGE ID       CREATED         SIZE
    go-hello-world   0.1       f3abf7ebc169   5 minutes ago   15.7MB

Now we're finally ready to run the rock and test the containerised Go
app:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use the same ``curl`` command as before to send a request to the Go
app's root endpoint which is running inside the container:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:curl-go-rock]
    :end-before: [docs:curl-go-rock-end]
    :dedent: 2

The Go app again responds with ``Hello, world!``.


View the app logs
~~~~~~~~~~~~~~~~~

When deploying the Go rock, we can always get the app logs with
:ref:`pebble_explanation_page`:

.. literalinclude:: code/go/task.yaml
    :language: text
    :start-after: [docs:get-logs]
    :end-before: [docs:get-logs-end]
    :dedent: 2

As a result, Pebble will give the logs for the
Go service running inside the container.
We should expect to see something similar to this:

.. terminal::

    2024-10-04T08:51:35.826Z [go] 2024/10/04 08:51:35 starting hello world application
    2024-10-04T08:51:39.974Z [go] 2024/10/04 08:51:39 new hello world request

We can also choose to follow the logs by using the ``-f`` option with the
``pebble logs`` command above. To stop following the logs, press :kbd:`Ctrl` + :kbd:`C`.


Stop the app
~~~~~~~~~~~~

Now we have a fully functional rock for a Go app! This concludes
the first part of this tutorial, so we'll stop the container and remove the
respective image for now:

.. literalinclude:: code/go/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2


Update the Go app
=================

As a final step, let's update our app. For example,
we want to add a new ``/time`` endpoint which returns the current time.

Start by opening the ``main.go`` file in a text editor and update the code to
look like the following:

.. literalinclude:: code/go/main.go.time
    :caption: ~/go-hello-world/main.go
    :language: go

Since we are creating a new version of the app, open the project
file and set ``version: '0.2'``.
The top of the ``rockcraft.yaml`` file should look similar to the following:

.. code-block:: yaml
    :caption: ~/go-hello-world/rockcraft.yaml
    :emphasize-lines: 6

    name: go-hello-world
    # see https://documentation.ubuntu.com/rockcraft/en/latest/explanation/bases/
    # for more information about bases and using 'bare' bases for chiselled rocks
    base: bare # as an alternative, a ubuntu base can be used
    build-base: ubuntu@24.04 # build-base is required when the base is bare
    version: '0.2'
    summary: A summary of your Go app # 79 char long summary
    description: |
        This is go-hello-world's description. You have a paragraph or two to tell the
        most important story about it. Keep it under 100 words though,
        we live in tweetspace and your description wants to look good in the
        container registries out there.
    # the platforms this rock should be built on and run on.
    # you can check your architecture with `dpkg --print-architecture`
    platforms:
        amd64:
        # arm64:
        # ppc64el:
        # s390x:

.. note::

    ``rockcraft pack`` will create a new image with the updated code even if we
    don't change the version. It is recommended to change the version whenever
    we make changes to the app in the image.

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

The updated app will respond with the current date and time.

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

We can also clean the Multipass instance up.
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

**App updates not taking effect?**

Upon changing the Go app and re-packing the rock, if
the changes are not taking effect, try running ``rockcraft clean`` and pack
the rock again with ``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/install-multipass
