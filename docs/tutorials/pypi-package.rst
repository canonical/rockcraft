Create a ROCK from a PyPI package
*********************************

By the end of this tutorial you will be able to run pyfiglet via docker:

.. code:: text

    $ docker run --rm -it pyfiglet:0.7.6 exec pyfiglet hello
     _          _ _
    | |__   ___| | | ___
    | '_ \ / _ \ | |/ _ \
    | | | |  __/ | | (_) |
    |_| |_|\___|_|_|\___/


Prerequisites
-------------
- snap enabled system (https://snapcraft.io)
- LXD installed (https://linuxcontainers.org/lxd/getting-started-cli/)
- skopeo installed (https://github.com/containers/skopeo).
  Skopeo will also be automatically installed as a Rockcraft dependency
- Docker installed (https://snapcraft.io/docker)
- Rockcraft installed
- a text editor


Project Setup
-------------

To create a new Rockcraft project, create a new directory and change into it:

.. literalinclude:: code/pyfiglet/task.yaml
    :language: bash
    :start-after: [docs:create-pyfiglet-dir]
    :end-before: [docs:create-pyfiglet-dir-end]
    :dedent: 2

Next, create a file called ``rockcraft.yaml`` with the following contents:

.. literalinclude:: code/pyfiglet/rockcraft.yaml
    :language: yaml


Pack the ROCK with Rockcraft
----------------------------

To build the ROCK, run:

.. literalinclude:: code/pyfiglet/task.yaml
    :language: bash
    :start-after: [docs:build-rock]
    :end-before: [docs:build-rock-end]
    :dedent: 2



Run the ROCK in Docker
----------------------

First, import the recently created ROCK into Docker:

.. literalinclude:: code/pyfiglet/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2


Now run the ``pyfiglet`` command from the ROCK:

.. literalinclude:: code/pyfiglet/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Which should print:

.. literalinclude:: code/pyfiglet/expected_output.txt
    :language: text


Explore the running container
-----------------------------

Since the ROCK uses an ubuntu base, you can poke around in a running container
using bash, via:

.. code:: yaml

    $ docker run --rm -it pyfiglet:0.7.6 exec bash
    root@14d1812a2681:/# pyfiglet hi
     _     _
    | |__ (_)
    | '_ \| |
    | | | | |
    |_| |_|_|

