.. _how-to-specify-a-base:

Specify a base
==============

Rocks are built on top of a software base, which determines compatibility with
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

For most Ubuntu-based rocks, select the latest LTS base, as your rock will benefit from
that release's 10-year support window.

If instead you need access to the features and packages of an interim Ubuntu base,
declare the interim release.


Bare base
---------

If you want to precisely control what's included in your rock and exclude the baseline
Ubuntu system, specify the bare base.

Even with the bare base, Rockcraft needs the software in an Ubuntu image to pack the
rock. This base is known as the *build* base. You must also set the special
``build-base`` key to an Ubuntu release.

Declare the bare base and its build base with:

.. code-block:: yaml
    :caption: snapcraft.yaml

    base: bare
    build-base: ubuntu@<version>

Your rock's contents might have dependencies that would normally be available in the
Ubuntu base. If they do, include them in your rock's parts.


Unmaintained bases
------------------

Over time, a rock's base will reach its end-of-life. It could be that the rock was
short-lived, meant for testing software during an interim base's comparatively short
nine-month lifecycle, or that it was extremely long-lived, and persisted past the
support window of its LTS base.

If you try and build a rock on an unmaintained base, even if it first built when the
base was supported, Rockcraft will by default halt the build.

If you know the risks of unmaintained bases, you can force the build to continue with:

.. code-block:: bash

    rockcraft pack --ignore=unmaintained
