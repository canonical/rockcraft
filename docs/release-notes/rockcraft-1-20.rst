.. meta::
    :description: Release notes for Rockcraft 1.20.

.. _release-1.20:

Rockcraft 1.20 release notes
============================

20 July 2026

Learn about the new features, changes, and fixes introduced in Rockcraft 1.20.
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

Rockcraft 1.20 brings the following features, integrations, and improvements.

``ubuntu@26.10`` base
~~~~~~~~~~~~~~~~~~~~~

Rockcraft now supports ``ubuntu@26.10`` as a base. Since this version of Ubuntu is in
development at the time of release, to select this base you must also set ``build-base: devel``.

FIPS Pebble
~~~~~~~~~~~

When packing a rock with a FIPS Ubuntu Pro service, Rockcraft now includes a FIPS version
of Pebble.

Documentation homepage
~~~~~~~~~~~~~~~~~~~~~~

The Rockcraft homepage has been revamped to better reflect the content of the documentation.

Minor features
--------------

Rockcraft 1.20 brings the following minor changes.

Support for ARMv8 in 32-bit mode (armv8l)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rockcraft no longer fails when the system is an ARMv8 running in 32-bit mode.

Documentation improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~

We've made improvements to the documentation:

* Clarified the minimum version of LXD to pack Pro rocks.
* Updated the tutorials to target base ``ubuntu@26.04``.
* Clarified the naming rules for platform keys.
* Incorporated user feedback on the 12-factor reference pages.

Contributors
------------

We would like to express a big thank you to all the people who contributed to this release.

:literalref:`@asanvaq <https://github.com/asanvaq>`,
:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@canon-cat <https://github.com/canon-cat>`,
:literalref:`@cmatsuoka <https://github.com/cmatsuoka>`,
:literalref:`@danielvnguyen <https://github.com/danielvnguyen>`,
:literalref:`@erinecon <https://github.com/erinecon>`,
:literalref:`@Gargoth <https://github.com/Gargoth>`,
:literalref:`@gcomneno <https://github.com/gcomneno>`,
:literalref:`@github-actions[bot] <https://github.com/github-actions[bot]>`,
:literalref:`@jahn-junior <https://github.com/jahn-junior>`,
:literalref:`@lengau <https://github.com/lengau>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@mr-cal <https://github.com/mr-cal>`,
:literalref:`@NiShITa-code <https://github.com/NiShITa-code>`,
:literalref:`@Pawansingh3889 <https://github.com/Pawansingh3889>`,
:literalref:`@PraaneshSelvaraj <https://github.com/PraaneshSelvaraj>`,
:literalref:`@smethnani <https://github.com/smethnani>`,
:literalref:`@steinbro <https://github.com/steinbro>`,
:literalref:`@TechWriterP <https://github.com/TechWriterP>`,
:literalref:`@tigarmo <https://github.com/tigarmo>`,
:literalref:`@zhijie-yang <https://github.com/zhijie-yang>`,
and :literalref:`@zlplzp123wyt <https://github.com/zlplzp123wyt>`.
