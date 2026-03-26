.. _release-1.16:

Rockcraft 1.16 release notes
============================

1 December 2025

Learn about the new features, changes, and fixes introduced in Rockcraft 1.16.
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

Rockcraft 1.16 brings the following features, integrations, and improvements.


``ubuntu@26.04`` base
~~~~~~~~~~~~~~~~~~~~~

Rockcraft now supports ``ubuntu@26.04`` as a base. Since this version of Ubuntu is in
development at time of release, to select this base you must also set
``build-base: devel``.


Stabilized ``ubuntu@25.10`` base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ubuntu@25.10`` base is now fully supported and no longer requires ``build-base:
devel``.


Availability on RISC-V 64-bit and armhf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rockcraft is once again available on RISC-V 64-bit and armhf systems.


JLink plugin
~~~~~~~~~~~~

The :ref:`craft_parts_jlink_plugin` supports two new keys.

- ``jlink-modules`` declares the complete list of modules to include in the OpenJDK
  image
- ``jlink-multi-release`` specifies the OpenJDK release version to use for multi-release
  JARs


Minor features
--------------

Rockcraft 1.16 brings the following minor changes.


Improved ``rockcraft.yaml`` Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We refreshed the rockcraft.yaml :ref:`reference <reference-rockcraft-yaml>`. The page
covers all keys, and their descriptions and examples are now sourced from the codebase,
so they will stay up-to-date as Rockcraft changes.

The reference has also been reorganized to better reflect idiomatic project file
structure and the new ``platforms`` keys.


Documentation for 12-factor app extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`set-up-web-app-rock` now contains the steps needed to override the rock's default
command that the 12-factor app extensions provide.


Backwards-incompatible changes
------------------------------

The following changes are incompatible with previous versions of Rockcraft.


Removed character support in platform names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`Platform <rockcraft-yaml-platform-keys>` names no longer support forward slashes
(/).


Fixed bugs and issues
---------------------

The following issues have been resolved in Rockcraft 1.16.


Rockcraft 1.16.0
~~~~~~~~~~~~~~~~

- `#992 <https://github.com/canonical/rockcraft/issues/992>`_ Architecture field in
  ``.rock/metadata.yaml`` is serialized incorrectly.
- `#1022 <https://github.com/canonical/rockcraft/issues/1022>`_ ``entrypoint-service``
  rejects empty argument list in 1.15 even though this previously worked


Contributors
------------

We would like to express a big thank you to all the people who contributed to
this release.

:literalref:`@asanvaq <https://github.com/asanvaq>`,
:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@erinecon <https://github.com/erinecon>`,
:literalref:`@jahn-junior <https://github.com/jahn-junior>`,
:literalref:`@javierdelapuente <https://github.com/javierdelapuente>`,
:literalref:`@lengau <https://github.com/lengau>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@steinbro <https://github.com/steinbro>`,
and :literalref:`@tigarmo <https://github.com/tigarmo>`.
