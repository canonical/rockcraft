Install slices in a rock
========================

In this tutorial, you will create a lean hello-world rock that uses chisel
slices, and then compare the resulting rock with the one created without slices
in :doc:`/tutorial/hello-world`.

Setup your environment
----------------------

.. include:: /reuse/tutorial/setup_stable.rst

Project setup
-------------

Create a new directory, write the following into a text editor and save it as
``rockcraft.yaml``:

.. _chisel-example:

.. literalinclude:: code/chisel/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

Note that this Rockcraft file uses the ``hello_bins`` Chisel slice to generate
an image containing only files that are strictly necessary for the ``hello``
binary. See :ref:`chisel_explanation` for details on the Chisel tool.


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
    Exported to OCI archive 'chiselled-hello_latest_amd64.rock'

The process might take a little while, but at the end, a new file named
``chiselled-hello_latest_amd64.rock`` will be present in the current directory.
That's your chiselled-hello rock, in oci-archive format.

Run the rock
------------

.. tabs::

    .. group-tab:: Docker

        First, import the recently created rock into Docker:

        .. literalinclude:: code/chisel/task.yaml
            :language: bash
            :start-after: [docs:skopeo-copy]
            :end-before: [docs:skopeo-copy-end]
            :dedent: 2

        Now run the ``hello`` command from the rock:

        .. literalinclude:: code/chisel/task.yaml
            :language: bash
            :start-after: [docs:docker-run]
            :end-before: [docs:docker-run-end]
            :dedent: 2

    .. group-tab:: Podman

        Run the oci archive directly using:

        .. literalinclude:: code/chisel/task.yaml
            :language: bash
            :start-after: [docs:podman-run]
            :end-before: [docs:podman-run-end]
            :dedent: 2

The output should be:

..  code-block:: text
    :class: log-snippets

    hello, world

The ``chiselled-hello`` image will have a size of 5.6 MB, which is much less in
size than the 8.8 MB ``hello`` rock created in :doc:`/tutorial/hello-world`.
