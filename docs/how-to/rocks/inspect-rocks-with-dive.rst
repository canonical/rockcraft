Inspect rocks with dive
***********************

`Dive`_ is a tool for analyzing and inspecting OCI container images.
It allows users to explore image layers, visualize how files are added,
modified, or removed across layers, and estimate the efficiency of an
image by calculating wasted space. As such, ``dive`` can help developers
optimize container images by identifying unnecessary bloat and improving
multi-stage builds.

Install and setup
===================

Dive can easily be installed via ``snap``, like so:

.. code-block:: bash

    $ sudo snap install dive
    $ sudo snap connect dive:docker-executables docker:docker-executables
    $ sudo snap connect dive:docker-daemon docker:docker-daemon

.. warning::

    You need to have ``docker`` installed as a snap as well in order for this
    method to work. If ``docker`` is installed via ``apt-get`` then you would
    need to install the .deb package. Check the `Installation guide`_.

A practical example
===================

Lets take the following rockcraft project file, where we create two
files during build and prime steps:

.. code-block:: yaml
    :caption: rockcraft.yaml

    name: dive-example
    version: "latest"
    summary: example to showcase dive tool
    description: shocase dive to inspect rocks
    base: ubuntu@24.04
    platforms:
    amd64:

    parts:
    test:
        plugin: nil
        override-build: |
        craftctl default
        echo "hello from build" > ${CRAFT_PART_INSTALL}/build-step
        override-prime: |
        craftctl default
        echo "hello from prime" > ${CRAFT_PRIME}/prime-step

We can pack the rock and copy it to docker daemon via skopeo:

.. code-block:: bash

    $ rockcraft pack
    $ sudo rockcraft.skopeo --insecure-policy copy oci-archive:dive-example_latest_amd64.rock docker-daemon:dive-example:latest

Then using ``dive`` we inspect the contents from the docker image:

.. code-block:: bash

    $ dive dive-example:latest

Under the layers section, we will find three layers:

.. code-block::

    │ Layers ├───────────────────────────────────────────────────────────────────
    Cmp   Size  Command
        78 MB  FROM blobs
        8.1 MB  umoci raw add-layer --image /root/images/dive-example:rockcraf...
        255 B  umoci raw add-layer --image /root/images/dive-example:latest /r...

* The first layer is the rock itself, made out of the base image declared in the
  ``base`` field
* The second layer adds configuration for :doc:`Pebble </explanation/pebble>` as well
  as the ``build-step`` and ``prime-step`` files we added in the ``override-build``
  and ``override-prime`` steps, respectively.
* The third layer adds metadata in ``/.rock/metadata.yaml``.

If we tell dive to show te aggregated changes (``Ctrl`` + ``A``) and select the third
layer, we can inspect the contents of the final image on the right side:

.. code-block::

    │ Aggregated Layer Contents ├─────────────────────────────────────────────
    Permission     UID:GID       Size  Filetree
    drwxr-xr-x         0:0      255 B  ├── .rock
    -rw-r--r--         0:0      255 B  │   └── metadata.yaml
    -rwxrwxrwx         0:0        0 B  ├── bin → usr/bin
    drwxr-xr-x         0:0        0 B  ├── boot
    -rw-r--r--         0:0       17 B  ├── build-step
    drwxr-xr-x         0:0        0 B  ├── dev
    drwxr-xr-x         0:0     108 kB  ├─⊕ etc
    drwxr-xr-x         0:0     4.8 kB  ├─⊕ home
    -rwxrwxrwx         0:0        0 B  ├── lib → usr/lib
    -rwxrwxrwx         0:0        0 B  ├── lib64 → usr/lib64
    drwxr-xr-x         0:0        0 B  ├── media
    drwxr-xr-x         0:0        0 B  ├── mnt
    drwxr-xr-x         0:0        0 B  ├── opt
    -rw-r--r--         0:0       17 B  ├── prime-step
    drwxr-xr-x         0:0        0 B  ├── proc
    drwx------         0:0     3.3 kB  ├─⊕ root
    drwxr-xr-x         0:0        7 B  ├─⊕ run
    -rwxrwxrwx         0:0        0 B  ├── sbin → usr/sbin
    drwxr-xr-x         0:0        0 B  ├── srv
    drwxr-xr-x         0:0        0 B  ├── sys
    drwxrwxrwx         0:0        0 B  ├── tmp
    drwxr-xr-x         0:0      83 MB  ├── usr
    drwxr-xr-x         0:0      27 MB  │   ├─⊕ bin
    drwxr-xr-x         0:0        0 B  │   ├── games
    drwxr-xr-x         0:0        0 B  │   ├── include
    drwxr-xr-x         0:0      48 MB  │   ├─⊕ lib
    drwxr-xr-x         0:0        0 B  │   ├─⊕ lib64
    drwxr-xr-x         0:0      19 kB  │   ├─⊕ libexec
    drwxr-xr-x         0:0        0 B  │   ├─⊕ local
    drwxr-xr-x         0:0     5.3 MB  │   ├─⊕ sbin
    drwxr-xr-x         0:0     2.9 MB  │   ├─⊕ share
    drwxr-xr-x         0:0        0 B  │   └── src
    drwxr-xr-x         0:0     3.2 MB  └─⊕ var

We can see that both ``build-step`` and ``prime-step`` files are present
at the root level.

.. _Dive: https://github.com/wagoodman/dive
.. _Installation guide: https://github.com/wagoodman/dive?tab=readme-ov-file#installation
