.. meta::
    :description: Learn to assemble a rock with Rockcraft. In this tutorial, we create a very small rock that prints a "Hello, world!" message to the log.

.. _tutorial-create-a-hello-world-rock:

Create a "Hello World" rock
===========================

This tutorial guides you through the process of packaging a rock with Rockcraft.

It should take around 10 minutes to complete.

Setup your environment
----------------------

.. include:: /reuse/tutorial/setup_stable.rst

Project setup
-------------

Rockcraft builds a rock for the architecture of your host, which you declare
in the ``platforms`` key of the project file. Start by checking the
architecture of your system:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:check-arch]
    :end-before: [docs:check-arch-end]
    :dedent: 2

Store the result in an environment variable, so that the commands later in
this tutorial can refer to it:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:set-arch]
    :end-before: [docs:set-arch-end]
    :dedent: 2

.. tip::
    Setting the architecture once like this saves you from typing it into
    every command that needs it, both in this tutorial and in your own
    projects. The commands below use ``$ARCH`` wherever the ``.rock``
    filename appears.

Create a new directory and write the following into a text editor and
save it as ``rockcraft.yaml``. If your architecture isn't ``amd64``, replace
``amd64`` under ``platforms`` with the value you got above:

.. literalinclude:: code/hello-world/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

This file instructs Rockcraft to build a rock that **only** has the ``hello`` package
(and its dependencies) inside. For more information about the ``parts`` section, check
:ref:`rockcraft-yaml-part-keys`. The remaining YAML keys correspond to metadata that
help define and describe the rock. For more information about all available keys, check
:ref:`reference-rockcraft-yaml`.

The ``name``, ``version`` and ``platform`` all influence the name of the
generated ``.rock`` file.

Pack the rock with Rockcraft
----------------------------

To build the rock, run:

.. literalinclude:: code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:build-rock]
    :end-before: [docs:build-rock-end]
    :dedent: 2

At the end of the process, a file named ``hello_latest_<architecture>.rock``
should be present in the current directory, for example
``hello_latest_amd64.rock`` on an ``amd64`` host. That's your rock, in
oci-archive format (a tarball).


Run the rock in Docker
----------------------

First, import the recently created rock into Docker, using the ``ARCH``
variable you set earlier:

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
