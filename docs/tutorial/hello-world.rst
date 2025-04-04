Create a "Hello World" rock
***************************

Setup your environment
----------------------

.. include:: /reuse/tutorial/setup_stable.rst

Project setup
-------------

Create a new directory and add a simple ``index.html`` file to it,
which will be included inside our rock afterwards.

.. literalinclude:: code/hello-world/index.html
    :caption: index.html
    :language: html

Now write the following into a text editor and save it as
``rockcraft.yaml``:

.. literalinclude:: code/hello-world/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

This file instructs Rockcraft to build a rock containing the ``index.html``
file. To do so, we use the :ref:`dump plugin <dump_plugin_explanation>`
to copy the files from the specified ``source`` into the staging area.

For more information about the ``parts`` section, check :ref:`part_properties`.
The remaining YAML keys correspond to metadata that help define and describe the rock.
For more information about all available keys, check :doc:`/reference/rockcraft.yaml`.

Pack the rock with Rockcraft
----------------------------

To build the rock, run:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:build-rock]
    :end-before: [docs:build-rock-end]
    :dedent: 2

The output should look as follows:

..  code-block:: text
    :emphasize-lines: 13
    :class: log-snippets

    Launching instance...
    Retrieved base bare for amd64
    Extracted bare:latest
    Executed: pull hello
    Executed: pull pebble
    Executed: overlay hello
    Executed: overlay pebble
    Executed: build hello
    Executed: build pebble
    Executed: stage hello
    Executed: stage pebble
    Executed: prime hello
    Executed: prime pebble
    Executed parts lifecycle
    Exported to OCI archive 'hello_latest_amd64.rock'

At the end of the process, a file named ``hello_latest_amd64.rock`` should be
present in the current directory. That's your rock, in oci-archive format
(a tarball).


Run the rock in Docker
----------------------

First, import the recently created rock into Docker:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Now you can use ``cat`` to verify the ``index.html`` file has been copied into
the rock:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

It should output the ``index.html`` file created before.
