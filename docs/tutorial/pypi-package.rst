.. _tutorial-pack-a-python-package:

Pack a Python package
=====================

By the end of this tutorial you will be able to run pyfiglet via docker:

.. code:: text

    $ docker run --rm -it pyfiglet:0.7.6 exec pyfiglet hello
     _          _ _
    | |__   ___| | | ___
    | '_ \ / _ \ | |/ _ \
    | | | |  __/ | | (_) |
    |_| |_|\___|_|_|\___/


Setup your environment
----------------------

.. include:: /reuse/tutorial/setup_stable.rst

Project setup
-------------

To create a new Rockcraft project, create a new directory and change into it:

.. literalinclude:: code/pyfiglet/task.yaml
    :language: bash
    :start-after: [docs:create-pyfiglet-dir]
    :end-before: [docs:create-pyfiglet-dir-end]
    :dedent: 2

Next, create a file called ``rockcraft.yaml`` with the following contents:

.. literalinclude:: code/pyfiglet/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

.. note::

    This example uses ``python`` plugin along ``python-packages``, so ``pip`` is
    invoked implicitly to install such packages. `PEP 668`_ changes the
    behaviour of Python package managers like ``pip`` by introducing a special
    marker (``EXTERNALLY-MANAGED``) that prevents ``pip`` from installing
    packages outside a virtual environment. Thus, ``python3-venv`` is required
    as a stage package.

Pack the rock with Rockcraft
----------------------------

To build the rock, run:

.. literalinclude:: code/pyfiglet/task.yaml
    :language: bash
    :start-after: [docs:build-rock]
    :end-before: [docs:build-rock-end]
    :dedent: 2

Run the rock in Docker
----------------------

First, import the recently created rock into Docker:

.. literalinclude:: code/pyfiglet/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2


Now run the ``pyfiglet`` command from the rock:

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

Since the rock uses an ubuntu base, you can poke around in a running container
using bash, via:

.. code:: yaml

    $ docker run --rm -it pyfiglet:0.7.6 exec bash
    root@14d1812a2681:/# pyfiglet hi
     _     _
    | |__ (_)
    | '_ \| |
    | | | | |
    |_| |_|_|

.. _`PEP 668`: https://peps.python.org/pep-0668/
