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
- skopeo installed (https://github.com/containers/skopeo)
- Docker installed (https://snapcraft.io/docker)
- Rockcraft installed
- a text editor


Project Setup
-------------

To create a new rock project,

.. code:: text

    mkdir pyfiglet-rock && cd pyfiglet-rock
    rockcraft init

Create a new directory and write the following into a text editor and
save it as ``rockcraft.yaml``:

.. literalinclude:: code/pyfiglet/rockcraft.yaml
    :language: yaml


Pack the ROCK with Rockcraft
----------------------------

To build the ROCK, run:

.. code:: text

    rockcraft clean && rockcraft pack -v

To copy the rock to the docker daemon, run:


Run the ROCK in Docker
----------------------

First, import the recently created ROCK into Docker:

.. code:: text

    skopeo --insecure-policy copy oci-archive:pyfiglet_0.7.6_amd64.rock docker-daemon:pyfiglet:0.7.6


Now run the ``pyfiglet`` command from the ROCK:

.. code:: text

    docker run --rm -it pyfiglet:0.7.6 exec pyfiglet it works!

Which should print:

.. code:: text

     _ _                        _        _
    (_) |_  __      _____  _ __| | _____| |
    | | __| \ \ /\ / / _ \| '__| |/ / __| |
    | | |_   \ V  V / (_) | |  |   <\__ \_|
    |_|\__|   \_/\_/ \___/|_|  |_|\_\___(_)


Explore the running container
-----------------------------

To be able to poke around the container, you could add ``bash`` to
`stage-packages`:

.. code:: yaml

    stage-packages:
      - bash


After repeating ``rockcraft pack`` and ``skopeo copy`` you should be able to
override the entrypoint:

.. code:: yaml

    $ docker run --rm -it --entrypoint bash pyfiglet:0.7.6
    root@14d1812a2681:/# pyfiglet hi
     _     _
    | |__ (_)
    | '_ \| |
    | | | | |
    |_| |_|_|

