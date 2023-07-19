Create a "Hello World" ROCK
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

This file instructs Rockcraft to build a ROCK that **only** has the ``hello``
binaries package slice (and its dependencies) inside, using
:ref:`chisel_explanation`. For more information about the ``parts``
section, check :ref:`ref_parts`. The remaining YAML fields correspond
to metadata that help define and describe the ROCK. For more
information about all available fields check :doc:`/reference/rockcraft.yaml`.

Pack the ROCK with Rockcraft
----------------------------

To build the ROCK, run:

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
    Created new layer
    Entrypoint set to ['/bin/pebble', 'enter', '--verbose']
    Labels and annotations set to ['org.opencontainers.image.version=1.0', 'org.opencontainers.image.title=hello', 'org.opencontainers.image.ref.name=hello', 'org.opencontainers.image.licenses=Apache-2.0', 'org.opencontainers.image.created=2023-07-13T14:55:46.049188+00:00', 'org.opencontainers.image.base.digest=93532f6b4812679c429e7415f60fc2260b070ffb744ec65298e65770e14bbe8d']
    Exported to OCI archive 'hello_1.0_amd64.rock'

At the end of the process, a file named ``hello_1.0_amd64.rock`` should be
present in the current directory. That's your ROCK, in oci-archive format
(a tarball).


Run the ROCK in Docker
----------------------

First, import the recently created ROCK into Docker:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Now run the ``hello`` command from the ROCK:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Which should print:

..  code-block:: text
    :class: foo

    hello, world
