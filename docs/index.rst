Rockcraft documentation
=======================

**Rockcraft is a tool to create** :ref:`rocks <explanation-rocks>` -- a new
generation of secure, stable and `OCI-compliant container images
<OCI_image_spec_>`_, based on Ubuntu.

**Rockcraft offers a truly declarative way for building efficient container images.** 
By making use of existing Ubuntu tools like LXD_ and Multipass_, Rockcraft
is able to compartmentalise typical container image builds into multiple
parts, each one being comprised of several independent lifecycle steps,
allowing complex operations to be declared at build time.

Rockcraft enables users to create automatically secure container images in sync with Ubuntu OS’s SLAs, 
whilst ensuring the smallest footprint possible.

**Rockcraft is for anyone who wants to build production-grade container images,
regardless of their experience as a software developer** -- from independent
software vendors to cloud-native developers and occasional container users.
Rockcraft handles all the repetitive and boilerplate steps of a build,
directing your focus to what really matters: the image's content.

In this documentation
---------------------

Getting started with Rockcraft
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Understand Rockcraft and build your first Rock.

* **Tutorial:** :ref:`Build your first rock in 15 min <tutorial-create-a-hello-world-rock>`
* **Basic concepts:** :ref:`Lifecycle details of a rock <craft-parts:lifecycle>`

Building rocks
~~~~~~~~~~~~~~

Configure, build, harden, and publish rocks with Rockcraft.

*  **Set up your rock:** :ref:`reference-rockcraft-yaml` • 
   :ref:`Types of bases <explanation-bases>` • :ref:`Specify a base <how-to-specify-a-base>` • 
   :ref:`Pebble as entrypoint <explanation-pebble>` • 
   :ref:`Convert an entrypoint to a Pebble layer <how-to-convert-an-entrypoint-to-a-pebble-layer>` • 
   :ref:`Define a non root user <how-to-add-an-internal-user>`
*  **Hardening:**  :ref:`Overview <explanation-chisel>` • :ref:`Chisel a rock <how-to-chisel-a-rock>` • 
   :ref:`Install a custom slice <how-to-install-a-custom-package-slice>` • 
   :ref:`Migrate a Docker image to a chiseled rock <how-to-migrate-a-docker-image-to-a-chiselled-rock>`
* **Remote builds:** :ref:`Build remotely using Launchpad<how-to-outsource-rock-builds-to-launchpad>`
*  **App rocks:** :ref:`Build a rock for an app <tutorial>` • 
   :ref:`Set-up 12-Factor rocks <set-up-web-app-rock>`• 
   :ref:`Use rocks for 12-Factor apps <use-web-app-rock>`
*  **Pack:** :ref:`Use the Rockcraft pack GitHub Action<how-to-use-the-rockcraft-pack-github-action>` • 
   :ref:`Pack a Python package <tutorial-pack-a-python-package>`
* **Publish:** :ref:`Publish a rock to a registry <how-to-publish-a-rock-to-a-registry>`

Rock components
~~~~~~~~~~~~~~~

Define how a rock is built and run.

* **Steps:** :ref:`ref_lifecycle_commands` • From prime step to OCI layer 
* **Parts:** Understand Parts • Filesets • Permissions
* **Extensions:** Extensions available  • :ref:`ref_extension_commands` • Configure the build base for an Express app 
* **Plugins:** Plugins available • Override a plugin's build • Include local files and remote resources using the dump plugin

.. toctree::
   :maxdepth: 1
   :hidden:

   tutorial/index
   how-to/index
   reference/index
   explanation/index
   contribute-to-this-documentation
   release-notes/index


.. grid:: 1 1 2 2

   .. grid-item-card:: :ref:`Tutorial <tutorial>`

      **Get started** - become familiar with Rockcraft by containerising different software applications as rocks.

   .. grid-item-card:: :ref:`How-to guides <how-to>`

      **Step-by-step guides** - learn key operations, ranging from :ref:`creating
      and cutting slices <how-to-chiselling>` to :ref:`migrating and publishing
      rocks <how-to-crafting>`.

.. grid:: 1 1 2 2
   :reverse:

   .. grid-item-card:: :ref:`Reference <reference>`

      **Technical information** - understand how to use every key in a project
      file.

   .. grid-item-card:: :ref:`Explanation <explanation>`

      **Discussion and clarification** - explore Rockcraft's lifecycle and how a
      rock gets packed under the hood.


Project and community
=====================

Rockcraft is a member of the Canonical family. It's an open source project
that warmly welcomes community projects, contributions, suggestions, fixes
and constructive feedback.

* `Ubuntu Rocks Discourse <https://discourse.ubuntu.com/c/project/rocks/117>`_
* `Rocks Community on Matrix <https://matrix.to/#/#rocks:ubuntu.com>`_
* `Ubuntu Code of Conduct <https://ubuntu.com/community/docs/ethos/code-of-conduct>`_
* `Canonical Contributor License Agreement
  <https://ubuntu.com/legal/contributors>`_
