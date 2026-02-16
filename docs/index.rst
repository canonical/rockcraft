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

Rockcraft enables users to create automatically secure container images in sync with Ubuntu releases,
whilst ensuring the smallest footprint possible.

**Rockcraft is for anyone who wants to build production-grade container images,
regardless of their experience as a software developer** -- from independent
software vendors to cloud-native developers and occasional container users.
Rockcraft handles all the repetitive and boilerplate steps of a build,
directing your focus to what really matters: the image's content.

In this documentation
---------------------

.. list-table::
    :widths: 35 65
    :header-rows: 0

    * - **Tutorial**
      - :ref:`Build your first rock <tutorial-create-a-hello-world-rock>`
    * - **Installation and setup**
      - :ref:`how-to-quickstart-guide`
    * - **Vocabulary and syntax**
      - :ref:`reference-commands` • :ref:`reference-rockcraft-yaml`
    * - **Platform compatibility**
      - :ref:`explanation-bases` • :ref:`how-to-specify-a-base` •
        :ref:`Build remotely using Launchpad<how-to-outsource-rock-builds-to-launchpad>`
    * - **Software integration**
      - :external+craft-parts:ref:`parts` • :ref:`reference-plugins` •
        :ref:`how-to-override-a-plugins-build` •
        :ref:`reference-extensions`
    * - **12-factor apps**
      - :ref:`tutorial-build-a-rock-for-a-django-app` • 
        :ref:`tutorial-build-a-rock-for-an-express-app` •
        :ref:`tutorial-build-a-rock-for-a-fastapi-app` •
        :ref:`tutorial-build-a-rock-for-a-flask-app` •
        :ref:`tutorial-build-a-rock-for-a-go-app` •
        :ref:`Set-up 12-Factor rocks <set-up-web-app-rock>` •
        :ref:`Use rocks for 12-Factor apps <use-web-app-rock>`
    * - **Process manager**
      - :ref:`Pebble as entrypoint <explanation-pebble>` •
        :ref:`Convert an entrypoint to a Pebble layer <how-to-convert-an-entrypoint-to-a-pebble-layer>`
    * - **Hardening**
      - :ref:`Chisel <explanation-chisel>` • 
        :ref:`Chisel rocks <how-to-chisel-a-rock>` •
        :ref:`Migrate Docker images to chiseled rocks <how-to-migrate-a-docker-image-to-a-chiselled-rock>` •
        :ref:`Install a custom slice <how-to-install-a-custom-package-slice>` •
        :ref:`Define a non root user <how-to-add-an-internal-user>`
    * - **Distribution**
      - :ref:`Publish a rock to a registry <how-to-publish-a-rock-to-a-registry>` •
        :ref:`Use the Rockcraft pack GitHub Action<how-to-use-the-rockcraft-pack-github-action>`

How this documentation is organized
-----------------------------------

This documentation uses the `Diátaxis documentation structure <https://diataxis.fr/>`_.

*  The :ref:`Tutorial <tutorial>` takes you step-by-step through building your first rock.
*  :ref:`How-to guides <how-to>` assume you have basic familiarity with Rockcraft.
   These include crafting rocks, building rocks for different apps and hardening.
* :ref:`Reference <reference>` provides a guide to the .yaml files, commands and components.
* :ref:`Explanation <explanation>` includes topic overviews, background and context and detailed discussion.

Project and community
---------------------

Rockcraft is a member of the Ubuntu family. It’s an open source project that warmly welcomes
`community contributions <https://documentation.ubuntu.com/project/contributors/>`_.

Support
~~~~~~~

* `Ubuntu Rocks Discourse <https://discourse.ubuntu.com/c/project/rocks/117>`_
* `Rocks Community on Matrix <https://matrix.to/#/#rocks:ubuntu.com>`_
* `Contribute to the project <https://github.com/canonical/rockcraft/blob/main/CONTRIBUTING.md>`_
* :ref:`Contribute to the documentation <contribute-to-this-documentation>`

Releases
~~~~~~~~

* :ref:`release-notes`

Governance and policies
~~~~~~~~~~~~~~~~~~~~~~~

* `Code of conduct <https://ubuntu.com/community/docs/ethos/code-of-conduct>`_
* `Security policy <https://github.com/canonical/rockcraft/blob/main/SECURITY.md>`_

Commercial support
~~~~~~~~~~~~~~~~~~

Thinking about using Rocks for your next project? `Get in touch!`_


.. toctree::
   :maxdepth: 1
   :hidden:

   tutorial/index
   how-to/index
   reference/index
   explanation/index
   contribute-to-this-documentation
   release-notes/index

.. _Get in touch!: https://canonical.com/#get-in-touch#
