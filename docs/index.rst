.. meta::
    :description: Documentation for Rockcraft, the tool for assembling rocks. Rocks are OCI-compliant images with extra security features and a smaller storage footprint.

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

.. domain::

    .. slice:: Get started

        :doc:`Build your first rock </tutorial/hello-world>`
        :doc:`Quickstart guide </how-to/get-started>`

    .. slice:: Base

        :doc:`Overview </explanation/bases>`
        :doc:`Specify a base </how-to/crafting/specify-a-base>`
        :doc:`Upgrade to the newest base </how-to/change-from-ubuntu2404-to-ubuntu2604>`

    .. slice:: Configuration

        :doc:`About parts </reference/parts-and-steps>`
        :doc:`rockcraft.yaml </reference/rockcraft-yaml>`

    .. slice:: Plugins

        :doc:`Override a plugin's build </how-to/crafting/override-a-plugins-build>`
        :doc:`Plugins available </reference/plugins>`

    .. slice:: Rockcraft CLI

        :doc:`Commands </reference/commands>`

    .. slice:: 12-factor apps

        :doc:`Flask tutorial </tutorial/flask>`
        :doc:`Django tutorial </tutorial/django>`
        :doc:`Go tutorial </tutorial/go>`
        :doc:`Express tutorial </tutorial/express>`
        :doc:`FastAPI tutorial </tutorial/fastapi>`
        :doc:`Spring Boot tutorial </tutorial/springboot>`
        :doc:`Extensions </reference/extensions/index>`
        :doc:`Set-up 12-Factor rocks </how-to/web-app-rocks/set-up-web-app-rock>`
        :doc:`Use rocks for 12-Factor apps </how-to/web-app-rocks/use-web-app-rock>`

    .. slice:: Process manager

        :doc:`Pebble as entrypoint </explanation/pebble>`
        :doc:`Convert an entrypoint to a Pebble layer </how-to/crafting/convert-to-pebble-layer>`

    .. slice:: Hardening

        :doc:`Chisel </explanation/chisel>`
        :doc:`Chisel rocks </how-to/chiseling/chisel-existing-rock>`
        :doc:`Migrate Docker images to chiseled rocks </how-to/crafting/migrate-to-chiselled-rock>`
        :doc:`Install a custom slice </how-to/chiseling/install-slice>`
        :doc:`Define a non root user </how-to/crafting/add-internal-user-to-a-rock>`

    .. slice:: Build workflows

        :doc:`Multi-architecture builds </how-to/crafting/outsource-rock-builds-to-launchpad>`
        :doc:`Pack a rock in a monorepo </how-to/crafting/pack-a-rock-in-a-monorepo>`

    .. slice:: Distribution

        :doc:`Use the Rockcraft pack GitHub Action </how-to/crafting/rockcraft-pack-action>`
        :doc:`Publish a rock to a registry </how-to/crafting/publish-a-rock>`

    .. slice:: Ubuntu Pro

        :doc:`Pack a Pro-compliant rock </how-to/crafting/pack-a-pro-rock>`

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

Get involved
~~~~~~~~~~~~

* `Ubuntu Rocks Discourse <https://discourse.ubuntu.com/c/project/rocks/117>`_
* `Rocks Community on Matrix`_
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
.. _Rocks Community on Matrix: https://matrix.to/#/#rocks:ubuntu.com
