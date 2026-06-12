.. meta::
    :description: Release notes for Rockcraft 1.19.

Rockcraft 1.19 release notes
============================

11 May 2026

Learn about the new features, changes, and fixes introduced in Rockcraft 1.19.
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

Rockcraft 1.19 brings the following features, integrations, and improvements.

Support for ubuntu\@26.04
~~~~~~~~~~~~~~~~~~~~~~~~~

Rockcraft now supports building rocks with the ubuntu\@26.04 base, which is stable
and recommended for all new rocks.

If you're currently using ubuntu\@24.04, you can migrate by following the
:ref:`how-to-migrate-2604` guide.

If you were already building experimental ubuntu\@26.04 rocks, you can drop
``build-base: devel`` from your project file.

Stabilization of 12-factor app extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The extensions providing support for the 12-factor app methodology using Express, FastAPI
and Go are now stable and no longer require setting the
``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS`` environment variable.

Bazel plugin
~~~~~~~~~~~~

The :ref:`craft_parts_bazel_plugin` supports building projects using the Bazel
build system, and is available for rocks targeting bases ubuntu\@25.10 and higher.

Contributors
------------

We would like to express a big thank you to all the people who contributed to this release.

:literalref:`@asanvaq <https://github.com/asanvaq>`,
:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@canon-cat <https://github.com/canon-cat>`,
:literalref:`@cmatsuoka <https://github.com/cmatsuoka>`,
:literalref:`@ethandcosta <https://github.com/ethandcosta>`,
:literalref:`@gcomneno <https://github.com/gcomneno>`,
:literalref:`@javierdelapuente <https://github.com/javierdelapuente>`,
:literalref:`@mateusrodrigues <https://github.com/mateusrodrigues>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@mr-cal <https://github.com/mr-cal>`,
:literalref:`@smethnani <https://github.com/smethnani>`,
:literalref:`@steinbro <https://github.com/steinbro>`,
and :literalref:`@tigarmo <https://github.com/tigarmo>`.
