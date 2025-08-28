.. _release-1.14:

..
    rockcraft
    docs: Incorporate UX feedback into 12-factor tutorials @erinecon (#918)
    docs: add CONTRIBUTING.md @medubelko (#925)
    fix: add missing migrate and migrate.sh @javierdelapuente (#932)
    feat: add entrypoint-command @alesancor1 (#939)

     name = "craft-application"
    -version = "5.4.0"
    +version = "5.7.1"

    feat(TestCommand): pack and test all packable platforms by @lengau in #807

     name = "craft-archives"
    -version = "2.1.0"
    +version = "2.2.0"

    fix: retry key receiving on port TCP/80 if using default keyserver by @upils in #189

     name = "craft-cli"
    -version = "3.0.0"
    +version = "3.1.2"

     name = "craft-grammar"
    -version = "2.0.3"
    +version = "2.2.0"

     name = "craft-parts"
    -version = "2.16.0"
    +version = "2.20.1"

    docs: add maven-use reference page by @bepri in #1179
    feat(jlink): introduce add_modules parameter by @vpa1977 in #1169
    fix(overlay): detect conflicts between overlay and install by @tigarmo in #1190

Rockcraft 1.14 release notes
============================

29 August 2025

Learn about the new features, changes, and fixes introduced in Rockcraft 1.14.
For information about the Rockcraft release cycle, see the
:ref:`release_policy_and_schedule`.


Requirements and compatibility
------------------------------

To run Rockcraft, a system requires the following minimum hardware and
installed software. These requirements apply to local hosts as well as VMs and
container hosts.


Minimum hardware requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- AMD64, ARM64, ARMv7-M, RISC-V 64-bit, PowerPC 64-bit little-endian, or S390x
  processor
- 2GB RAM
- 10GB available storage space
- Internet access for remote software sources and the Snap Store


Platform requirements
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
  :header-rows: 1
  :widths: 1 3 3

  * - Platform
    - Version
    - Software requirements
  * - GNU/Linux
    - Popular distributions that ship with systemd and are `compatible with
      snapd <https://snapcraft.io/docs/installing-snapd>`_
    - systemd


What's new
----------

Rockcraft 1.14 brings the following features, integrations, and improvements.

New ``entrypoint-command`` project key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This key defines the rock's OCI entrypoint, bypassing the default Pebble-powered 
entrypoint. It can be necessary for cases like OS and base images, where
an application-centric Pebble service is inadequate.

See the :ref:`rockcraft.yaml reference <rockcraft-yaml-entrypoint-command>` for usage 
details.

Minor features
--------------

Rockcraft 1.14 brings the following minor changes.

Improved ``test`` command
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``test`` command now packs and tests all platforms that can be built on the running
environment.

Improved keyserver support in ``package-repositories``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If an attempt to connect to the default keyserver to retrieve a public key fails, the
``package-repositories`` mechanism will now try to connect through port 80
while also respecting proxy addresses set via the standard ``http_proxy`` and
``https_proxy`` environment variables.

New ``jlink-extra-modules`` key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The new ``jlink-extra-modules`` key in the :ref:`craft_parts_jlink_plugin` defines 
modules to add to the generated OpenJDK image.

Improved conflict detection between the overlay and build steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The collision resolution during the stage step now takes into account the contents
of the overlay.

Improved documentation for 12-factor app extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tutorial and reference pages for all 12-factor app extensions were improved
based on user feedback, with fixes to multiple steps that were showstoppers.

New ``maven-use`` plugin reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the documentation, we added a :ref:`craft_parts_maven_use_plugin` reference.

Clarified contribution guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've added a `CONTRIBUTING.md`_ file describing the general approach and guidelines for
contributing to the Rockcraft codebase. If you have an idea for an improvement, be sure
to check it out.

Contributors
------------

We would like to express a big thank you to all the people who contributed to
this release.

:literalref:`@alesancor1<https://github.com/alesancor1>`,
:literalref:`@bepri<https://github.com/bepri>`,
:literalref:`@erinecon<https://github.com/erinecon>`,
:literalref:`@jahn-junior<https://github.com/jahn-junior>`,
:literalref:`@javierdelapuente<https://github.com/javierdelapuente>`,
:literalref:`@medubelko<https://github.com/medubelko>`,
and :literalref:`@tigarmo<https://github.com/tigarmo>`.

.. _CONTRIBUTING.md: https://github.com/canonical/rockcraft/blob/main/CONTRIBUTING.md
