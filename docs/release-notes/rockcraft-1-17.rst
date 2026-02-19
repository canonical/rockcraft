.. meta::
    :description: Learn about notable features, fixes and documentation updates in Rockcraft 1.17.

.. _release-1.17:

Rockcraft 1.17 release notes
============================

9 February 2026

Learn about the new features, changes, and fixes introduced in Rockcraft 1.17.
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

Rockcraft 1.17 brings the following features, integrations, and improvements.


Gradle plugin
~~~~~~~~~~~~~

The :ref:`craft_parts_gradle_plugin` now supports the ``self-contained`` :ref:`build-attribute <partspec.build_attributes>`,
to allow building Gradle projects from dependencies that are fully declared in the Rockcraft project file.

Additionally, the plugin now supports the ``gradle-use-daemon`` key, which enables
the Gradle Daemon during build.


Project schema included in snap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The JSON Schema for the ``rockcraft.yaml`` project file is now included in the Rockcraft
snap. The schema is located at the ``schema/rockcraft.json`` path inside the snap.


Python compilation with the uv plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :ref:`craft_parts_uv_plugin` now compiles Python bytecode by default. This is desirable for most projects, as it
improves the startup time of Python apps. To disable bytecode compilation, set the ``UV_COMPILE_BYTECODE``
environment variable to ``0`` in the part's :ref:`build-environment <partspec.build_environment>` key.


Minor features
--------------

Rockcraft 1.17 brings the following minor changes.


Better support for parent POMs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Maven-based plugins now correctly support projects where the ``groupId`` is defined
in a parent POM.


12-factor app rocks
~~~~~~~~~~~~~~~~~~~

The init profiles for the 12-factor app extensions now use ``bare`` bases, which
makes leaner rocks by default and reduces the attack surface for vulnerabilities.

Additionally, rocks created with a 12-factor app extension now include a command interpreter
on ``/bin/sh``, which allows them to work correctly with the ``juju ssh`` command.


Documentation improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~

We've made improvements to the documentation:

- Corrected the output of the :ref:`"Hello World" tutorial <tutorial-create-a-hello-world-rock>`.
- Fixed various broken links across the documentation.
- Updated the warning about the interaction between Docker and LXD instances.


Fixed bugs and issues
---------------------

The following issues have been resolved in Rockcraft 1.17.


Rockcraft 1.17.0
~~~~~~~~~~~~~~~~

- `#1069 <https://github.com/canonical/rockcraft/issues/1069>`__ schema: ubuntu\@26.04 should not be a valid build-base for now.
- `craft-application #986 <https://github.com/canonical/craft-application/issues/986>`__ craft-application is using outdated distro-support package.

Contributors
------------

We would like to express a big thank you to all the people who contributed to
this release.

:literalref:`@asanvaq <https://github.com/asanvaq>`,
:literalref:`@alithethird <https://github.com/alithethird>`,
:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@canon-cat <https://github.com/canon-cat>`,
:literalref:`@cjdcordeiro <https://github.com/cjdcordeiro>`,
:literalref:`@cmatsuoka <https://github.com/cmatsuoka>`,
:literalref:`@erinecon <https://github.com/erinecon>`,
:literalref:`@Guillaumebeuzeboc <https://github.com/Guillaumebeuzeboc>`,
:literalref:`@Guno327 <https://github.com/Guno327>`,
:literalref:`@javierdelapuente <https://github.com/javierdelapuente>`,
:literalref:`@jahn-junior <https://github.com/jahn-junior>`,
:literalref:`@jonathan-conder <https://github.com/jonathan-conder>`,
:literalref:`@lengau <https://github.com/lengau>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@smethnani <https://github.com/smethnani>`,
:literalref:`@steinbro <https://github.com/steinbro>`,
:literalref:`@tigarmo <https://github.com/tigarmo>`,
and :literalref:`@zhijie-yang <https://github.com/zhijie-yang>`.
