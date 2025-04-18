.. _chisel_existing_rock:

How to chisel an existing rock
******************************

Having additional utilities inside a rock can be useful for development and
testing purposes. However, when moving to production, you want to make your
rock as lean and secure as possible, getting rid of all the unnecessary bits
and thus reducing its attack surface, while retaining its functionality.

For this, you'll want to ensure that your rock has a ``bare``
:ref:`base <rockcraft_yaml_base>` and that its contents are
:ref:`chiselled <chisel_explanation>`.

For this guide, let's take the example of a Python runtime rock.

A Python rock
-------------

Our starting point is an Ubuntu 22.04-based Python rock, described by the
following project file:

.. literalinclude:: ../code/chisel-existing-rock/rock/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

This rock can be built by running:

.. literalinclude:: ../code/chisel-existing-rock/task.yaml
    :language: bash
    :start-after: [docs:pack-rock]
    :end-before: [docs:pack-rock-end]
    :dedent: 2

The resulting rock (``python_3.11_amd64.rock``) will have approximately
**42MB** and have a functional Python3.11 interpreter. You can verify that by
running a very simply "Hello, world" Python script in it:

.. tabs::

    .. group-tab:: Docker

        Using Docker:

        .. literalinclude:: ../code/chisel-existing-rock/task.yaml
            :language: bash
            :start-after: [docs:run-rock]
            :end-before: [docs:run-rock-end]
            :dedent: 2

    .. group-tab:: Podman

        Using Podman:

        .. literalinclude:: ../code/chisel-existing-rock/task.yaml
            :language: bash
            :start-after: [docs:run-rock-podman]
            :end-before: [docs:run-rock-podman-end]
            :dedent: 2

This rock will also have other utilities like ``bash`` and ``apt`` which come
from the rock's underlying Ubuntu 22.04 base.

Rebuild the rock with a ``bare`` base
-------------------------------------

When starting to prepare the rock for production, the main goal is to get rid
of all the software that is not necessary at runtime, and the first step
towards achieving that goal is to use a ``bare`` base.

In a separate directory, copy the contents of ``rockcraft.yaml`` from above and
replace ``base: ubuntu@22.04`` with ``base: bare``. With this change, you must
also remember to tell Rockcraft which Ubuntu release to use for its build
environment. Do this by adding ``build-base: ubuntu@22.04`` to the
project file, which should now look like this:

.. literalinclude:: ../code/chisel-existing-rock/bare-rock/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

Pack this rock with the same ``rockcraft`` command as above:

.. literalinclude:: ../code/chisel-existing-rock/task.yaml
    :language: bash
    :start-after: [docs:pack-bare-rock]
    :end-before: [docs:pack-bare-rock-end]
    :dedent: 2

This new rock (``bare-python_3.11_amd64.rock``) will now have about **28MB** -
a ~33% size reduction - and also have a functional Python3.11 interpreter.
Run the same "Hello, world" Python script as before to confirm:

.. tabs::

    .. group-tab:: Docker

        With Docker:

        .. literalinclude:: ../code/chisel-existing-rock/task.yaml
            :language: bash
            :start-after: [docs:run-bare-rock]
            :end-before: [docs:run-bare-rock-end]
            :dedent: 2

    .. group-tab:: Podman

        With Podman:

        .. literalinclude:: ../code/chisel-existing-rock/task.yaml
            :language: bash
            :start-after: [docs:run-bare-rock-podman]
            :end-before: [docs:run-bare-rock-podman-end]
            :dedent: 2

The question then is: *how is rockcraft able to produce an equally functional
Python rock with such a drastic reduction in size?*

And the answer is: *the rock no longer has the Ubuntu base as its first layer,
and thus no longer has utilities like ``bash`` and ``apt`` (which aren't needed
for this use case anyway)!*

Chisel the Python rock
----------------------

The last step in your way to production is to chisel the rock in order to
further reduce its size and attack surface, by stripping down the internal
Python components that are not needed for the final application.

In this example, the Python application is a very simple "Hello, world", which
means we need nothing else but the core Python modules. For that, copy the
previous ``rockcraft.yaml`` to a new directory and simply append the desired
package slice names to the list of ``stage-packages``, like this:

.. literalinclude:: ../code/chisel-existing-rock/chiselled-rock/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

Pack it with:

.. literalinclude:: ../code/chisel-existing-rock/task.yaml
    :language: bash
    :start-after: [docs:pack-chiselled-rock]
    :end-before: [docs:pack-chiselled-rock-end]
    :dedent: 2

And the end result will be an astoundingly small Python rock with **13MB**!
And the "Hello, world" script still works:

.. tabs::

    .. group-tab:: Docker

        With Docker:

        .. literalinclude:: ../code/chisel-existing-rock/task.yaml
            :language: bash
            :start-after: [docs:run-chiselled-rock]
            :end-before: [docs:run-chiselled-rock-end]
            :dedent: 2

    .. group-tab:: Podman

        With Podman:

        .. literalinclude:: ../code/chisel-existing-rock/task.yaml
            :language: bash
            :start-after: [docs:run-chiselled-rock-podman]
            :end-before: [docs:run-chiselled-rock-podman-end]
            :dedent: 2

**To conclude**, you've just created a general-purpose Python rock with just a
few YAML lines and no code whatsoever! Then, by changing a couple of YAML
fields (the ``base``), you've achieved a **~33% size reduction** while
maintaining functionality. Finally, by appending two words (literally, just
the slice names) to the project file, you were able to reduce the rock's
size even further by an **additional ~37%** of its original size! In short:

+---------------+------------------+-----------+
| Original rock | w/ ``bare`` base | chiselled |
+===============+==================+===========+
| 42MB          | 28MB             | 13MB      |
+---------------+------------------+-----------+
