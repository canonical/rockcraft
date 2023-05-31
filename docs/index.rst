Welcome to Rockcraft's documentation!
===========================================

**Rockcraft is a tool to create** :ref:`rocks_explanation` -- a new generation
of secure, stable and `OCI-compliant container images <OCI_image_spec_>`_,
based on Ubuntu.

**Rockcraft is for anyone who wants to build production-grade container images,
regardless of their experience as a software developer** -- from independent
software vendors to cloud-native developers and occasional container users.
Rockcraft handles all the repetitive and boilerplate steps of a build,
directing your focus to what really matters: the image's content.

**Using the same language as Snapcraft and Charmcraft, Rockcraft
offers a truly declarative way for building efficient container images.**
By making use of existing Ubuntu tools like LXD_ and Multipass_, Rockcraft
is able to compartmentalise typical container image builds into multiple
parts, each one being comprised of several independent lifecycle steps,
allowing complex operations to be declared at build time.

.. toctree::
   :maxdepth: 1
   :hidden:

   tutorials/index
   how-to/index
   reference
   explanation/index


.. grid:: 1 1 2 2

   .. grid-item-card:: :ref:`Tutorial <tutorial>`

      **Get started** with a hands-on introduction to Rockcraft

   .. grid-item-card:: :ref:`How-to guides <how-to>`

      **Step-by-step guides** covering key operations and common tasks

.. grid:: 1 1 2 2
   :reverse:

   .. grid-item-card:: :ref:`Reference <reference>`

      **Technical information** about the ``rockcraft.yaml`` format

   .. grid-item-card:: :ref:`Explanation <explanation>`

      **Discussion and clarification** of key topics


Project and community
=====================

Rockcraft is a member of the Canonical family. It's an open source project
that warmly welcomes community projects, contributions, suggestions, fixes
and constructive feedback.

* `Ubuntu Code of Conduct <https://ubuntu.com/community/code-of-conduct>`_.
* `Canonical contributor license agreement
  <https://ubuntu.com/legal/contributors>`_.

.. include:: /links.txt

