.. _tutorial-create-a-hello-world-rock:

Create a "Hello World" rock
===========================

Setup your environment
----------------------

.. include:: /reuse/tutorial/setup_stable.rst

Project setup
-------------

Create a new directory and write the following into a text editor and
save it as ``rockcraft.yaml``:

.. literalinclude:: code/hello-world/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

This file instructs Rockcraft to build a rock that **only** has the ``hello`` package
(and its dependencies) inside. For more information about the ``parts`` section, check
:ref:`rockcraft-yaml-part-keys`. The remaining YAML keys correspond to metadata that
help define and describe the rock. For more information about all available keys, check
:ref:`reference-rockcraft-yaml`.

.. admonition:: About the build base

   The rock in this tutorial depends on ``build-base: ubuntu@22.04``.
   It may not build if you use a different Ubuntu base, such as
   ``ubuntu@24.04``, because the contents of ``stage-packages``
   can vary between releases.

Pack the rock with Rockcraft
----------------------------

To build the rock, run:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:build-rock]
    :end-before: [docs:build-rock-end]
    :dedent: 2

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

Now run the ``hello`` command from the rock:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Which should print:

..  code-block:: text
    :class: log-snippets

    hello, world
