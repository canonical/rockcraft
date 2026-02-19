.. _release-1.9.0:
.. _release-1.9:

Rockcraft 1.9 release notes
===========================

28 February 2025

Learn about the new features, changes, and fixes introduced in Rockcraft 1.9.
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

Rockcraft 1.9 brings the following features, integrations, and improvements.

Remote build improvements
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``remote-build`` command now displays builds that have been created but are still
pending. Additionally, the Launchpad project can be specified through the new
``--project`` parameter.

Improved support for build-packages for cross-compilation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rockcraft projects that perform cross-compilation can now declare packages of the target
architecture in the ``build-packages`` key.

Documentation improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~

The terminology around the ``rockcraft.yaml`` project file has been cleaned up, and the
**Give Feedback** button has been restored to its location at the the top of the page.


Contributors
------------

We would like to express a big thank you to all the people who contributed to
this release.

:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@erinecon <https://github.com/erinecon>`,
:literalref:`@medubelko <https://github.com/medubelko>`.
and :literalref:`@s-makin <https://github.com/s-makin>`.
