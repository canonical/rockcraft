Install slices in a rock
========================

In this tutorial, you will create a lean rock that contains a fully functional
OpenSSL installation, and you will verify that it is functional by loading the
rock into Docker and using it to validate the certificates of the Ubuntu
website.

Prerequisites
-------------

- snap enabled system (https://snapcraft.io)
- LXD installed (https://linuxcontainers.org/lxd/getting-started-cli/)
- skopeo installed (https://github.com/containers/skopeo)
- Docker installed (https://docs.docker.com/get-docker/)
- a text editor


Install Rockcraft
-----------------

Install Rockcraft on your host:

.. literalinclude:: code/chisel/task.yaml
    :language: bash
    :start-after: [docs:install-rockcraft]
    :end-before: [docs:install-rockcraft-end]
    :dedent: 2


Project Setup
-------------

Create a new directory, write the following into a text editor and save it as
``rockcraft.yaml``:

.. _chisel-example:

.. literalinclude:: code/chisel/rockcraft.yaml
    :language: yaml

Note that this Rockcraft file uses the ``hello_bins`` Chisel slice to generate
an image containing only files that are strictly necessary for hello binary. See
:ref:`chisel_explanation` for details on the Chisel tool.


Pack the rock with Rockcraft
----------------------------

To build the rock, run:

.. literalinclude:: code/chisel/task.yaml
    :language: bash
    :start-after: [docs:build-rock]
    :end-before: [docs:build-rock-end]
    :dedent: 2

The output will look similar to:

..  code-block:: text
    :emphasize-lines: 10
    :class: log-snippets

    Launching instance...
    Retrieved base bare for amd64
    Extracted bare:latest
    Executed: pull hello
    Executed: overlay hello
    Executed: build hello
    Executed: stage hello
    Executed: prime hello
    Executed parts lifecycle
    Exported to OCI archive 'chisel-hello_1.0_amd64.rock'

The process might take a little while, but at the end, a new file named
``chisel-hello_1.0_amd64.rock`` will be present in the current directory.
That's your OpenSSL rock, in oci-archive format.

Run the rock in Docker
----------------------

First, import the recently created rock into Docker:

.. literalinclude:: code/chisel/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Now you can run a container from the rock:

.. literalinclude:: code/chisel/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Which should print:

..  code-block:: text
    :class: foo

    hello, world

The ``slice-hello`` image will have a size of ~5MB, which is 67% less in size
than the ``hello`` image that has size of ~15MB and which was created in
:doc:`/tutorials/hello-world`.
