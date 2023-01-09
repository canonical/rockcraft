.. |h4| raw:: html

   <h4>

.. |h4end| raw:: html

   </h4>

.. |br| raw:: html

   <br />

Welcome to Rockcraft's documentation!
===========================================


**Rockcraft is a tool to create ROCKs** - a new generation of secure, stable
and OCI-compliant container images, powered by Ubuntu.

**Using the same language as Snapcraft and Charmcraft,** Rockcraft (currently
under heavy development) offers a true declarative way for building efficient
container images. By making use of existing Ubuntu tools like LXD and Multipass,
Rockcraft is able to compartmentalize your typical container image build into
multiple parts, each one being comprised of several independent lifecycle
steps (pull, build, stage and prime), allowing you to declaratively perform
complex operations, at build time, without the need for massaging or
stripping down the build environment from where your final container image
originates.

**Off with the cumbersome and explicit scripting, on with the new declarative
builds.** While preserving the familiar Ubuntu experience, Rockcraft
eliminates the need for imperative builds, allowing everyone to declaratively
define a container image that is built from Ubuntu, for Ubuntu users.
Rockcraft implements source-to-image best-practice designs, handling all the
repetitive and boilerplate steps of a build and directing your focus to what
really matters - the image's content.

**Rockcraft is for everyone wanting to build production-grade container
images,** regardless of their experience as a software developer. From
independent software vendors to cloud-native developers and occasional
container users.


.. toctree::
   :maxdepth: 1
   :hidden:

   tutorials/index
   how-to/index
   reference
   explanation


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
* `Canonical contributor licenses agreement
  <https://ubuntu.com/legal/contributors>`_.

