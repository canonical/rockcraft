Create a "Hello World" rock
***************************

Prerequisites
-------------
- snap enabled system (https://snapcraft.io)
- LXD installed (https://linuxcontainers.org/lxd/getting-started-cli/)
- skopeo installed (https://github.com/containers/skopeo)
- Docker installed (https://snapcraft.io/docker)
- a text editor


Install Rockcraft
-----------------

Install Rockcraft on your host:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:install-rockcraft]
    :end-before: [docs:install-rockcraft-end]
    :dedent: 2

Project Setup
-------------

Create a new directory and write the following into a text editor and
save it as ``rockcraft.yaml``:

.. literalinclude:: code/hello-world/rockcraft.yaml
    :language: yaml

This file instructs Rockcraft to build a rock that **only** has the ``hello``
binaries package slice (and its dependencies) inside, using
:ref:`chisel_explanation`. For more information about the ``parts``
section, check :ref:`ref_parts`. The remaining YAML fields correspond
to metadata that help define and describe the rock. For more
information about all available fields check :doc:`/reference/rockcraft.yaml`.

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
    Exported to OCI archive 'hello_1.0_amd64.rock'

At the end of the process, a file named ``hello_1.0_amd64.rock`` should be
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

Now run the ``hello`` command from the rock:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Which should print:

..  code-block:: text
    :class: foo

    hello, world
