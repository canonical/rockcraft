.. meta::
    :description: How to pack a rock located in a monorepo structure with shared dependencies.

.. _how-to-pack-a-rock-in-a-monorepo:

Pack a rock in a monorepo
=========================

By default, Rockcraft isolates the build environment to the directory containing
the project file. When building in managed environments, such as LXD containers or
virtual machines, files outside the rock's directory are not copied into the build
instance.

With experimental monorepo support enabled, Rockcraft detects the root of the enclosing
Git repository and mounts the entire repository into the build environment. Parts can then
access parent and sibling directories.

Prerequisites
-------------

- A Git repository containing your rock and shared assets
- Rockcraft 1.21 or higher


Declare project directories
---------------------------

Consider a rock monorepo that looks as follows:

.. code-block:: text

    my-monorepo/
    ├── .git/
    ├── shared/
    │   └── common.h
    └── rocks/
        ├── 24.04/
        │   ├── rockcraft.yaml
        │   ├── Makefile
        │   └── main.c
        └── 26.04/
            ├── rockcraft.yaml
            ├── Makefile
            └── main.c

For rocks located in subdirectories of your repository, set the ``source`` key of
each rock's main part to the relative path of the repository root and the
``source-subdir`` key to the directory containing the rock's project file.

For the rock in the example repository shown previously, these keys would be
declared as:

.. code-block:: yaml
    :caption: rocks/26.04/rockcraft.yaml
    :emphasize-lines: 9,10

    name: my-rock
    base: ubuntu@26.04
    platforms:
      amd64:

    parts:
      my-rock:
        plugin: make
        source: ../..
        source-subdir: rocks/26.04

.. note::

    For repositories with the ``rockcraft.yaml`` file at the root and the rock source
    in a subdirectory, you do not need to enable monorepo support. Instead, declare the
    ``source-subdir`` key in the rock's main part.

With the whole repository mounted in the build instance, Rockcraft can reference the
``../shared/common.h`` file exactly as it would outside of Rockcraft.


Pack the rock
-------------

To pack the rock using the monorepo root as the build root, set the
``ROCKCRAFT_EXPERIMENTAL_MONOREPO`` environment variable when invoking
``rockcraft pack``:

.. code-block:: bash

    cd rocks/26.04/
    ROCKCRAFT_EXPERIMENTAL_MONOREPO=1 rockcraft pack

Rockcraft will mount the root of the Git repository into the build instance and build the
rock with access to the shared files.
