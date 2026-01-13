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

* **Steps:** :ref:`ref_lifecycle_commands` • :ref:`expl_prime_step_OCI_layer` 
* **Parts:** :ref:`Understand Parts <craft-parts:parts>` • :ref:`craft-parts:filesets_explanation` • :ref:`Permissions <reference-parts-and-steps>`
*  **Extensions:** :ref:`Extensions available <reference-extensions>` • :ref:`ref_extension_commands` • 
   :ref:`configure-the-build-base-for-an-express-app` 
*  **Plugins:** :ref:`Plugins available <reference-plugins>` • 
   :ref:`Include local files and remote resources using the dump plugin <craft-parts:how_to_include_files_and_resources>`

How this documentation is organized
-----------------------------------

*  The :ref:`Tutorial <tutorial>` takes you step-by-step through building your first rock.
*  :ref:`How-to guides <how-to>` assume you have basic familiarity with Rockcraft. 
   These include crafting rocks, building rocks for different apps and hardening.
* :ref:`Reference <reference>` provides a guide to the .yaml files, commands and components.
* :ref:`Explanation <explanation>` includes topic overviews, background and context and detailed discussion.

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


This documentation uses the `Diátaxis documentation structure <https://diataxis.fr/>`_.


.. toctree::
   :maxdepth: 1
   :hidden:

   tutorial/index
   how-to/index
   reference/index
   explanation/index
   contribute-to-this-documentation
   release-notes/index