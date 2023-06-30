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
    Retrieved base ubuntu:20.04
    Extracted ubuntu:20.04
    Executed: pull hello
    Executed: overlay hello
    Executed: build hello
    Executed: stage hello
    Executed: prime hello
    Executed parts lifecycle
    Created new layer
    Entrypoint set to ['/bin/pebble', 'enter', '--verbose']
    Labels and annotations set to ['org.opencontainers.image.version=1.0', 'org.opencontainers.image.title=hello', 'org.opencontainers.image.ref.name=hello', 'org.opencontainers.image.licenses=Apache-2.0', 'org.opencontainers.image.created=2023-06-27T06:56:11.647650+00:00', 'org.opencontainers.image.base.digest=d72c6818d7682fe5e71ad947c11a36c2fade3f004b6b353b9885de2bd37b71d6']
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
