.. _how-to-specify-a-base:

Specify a base
==============

All rocks are layered on top of a software base, which determines compatibility with
their contents. When you craft a rock, you must specify its base, because it can't
assume a default base.

Bases are either an :ref:`Ubuntu LTS or interim release
<explanation-bases-lts-and-interim-bases>`, or the :ref:`bare base
<explanation-bases-bare-bases>`.


Ubuntu LTS and interim bases
----------------------------

Specify an Ubuntu base with:

.. code-block:: yaml
    :caption: rockcraft.yaml

    base: ubuntu@<version>

For most rocks, select the latest Ubuntu LTS base, as your rock will benefit from that
release's 10-year support window.

If instead you need access to the features and packages of an interim Ubuntu base,
declare the interim release.


Unmaintained bases
------------------

Over time, a rock's base will reach its end-of-life. It could be that the rock was
short-lived, meant for testing software during an interim base's comparatively short
nine-month lifecycle, or that it was extremely long-lived, and persisted past the
support window of its LTS base.

If you try and build a rock on an unsupported base, even if it first built when the base
was supported, Rockcraft will by default halt the build. If you know the risks of
unsupported bases, you can force the build to continue with:

.. code-block:: bash

    rockcraft pack --ignore=unmaintained


Bare base
---------

A bare base is a special base for when you need a very lightweight rock. Declare the
bare base with:

.. code-block:: yaml
    :caption: snapcraft.yaml

    base: bare
