.. _release-1.10:

Rockcraft 1.10 release notes
============================

4 April 2025

Learn about the new features, changes, and fixes introduced in Rockcraft 1.10.
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

Rockcraft 1.10 brings the following features, integrations, and improvements.


ExpressJS extension
~~~~~~~~~~~~~~~~~~~

The new ExpressJS extension streamlines the process of building rocks that bundle
ExpressJS applications. This extension makes it easy to install your application's
dependencies, including the Node.js interpreter and NPM.

This new extension is experimental and subject to change. For more information, check
out the Express :ref:`tutorial <tutorial-build-a-rock-for-an-express-app>` and
:ref:`reference <reference-express-framework>`.


Minor features
--------------

Rockcraft 1.10 brings the following minor changes.

Part sources
~~~~~~~~~~~~

The :ref:`source-commit <PartSpec.source_commit>` key now accepts short hashes in
addition to the full hash of a Git commit.

OCI Annotations
~~~~~~~~~~~~~~~

Generated rocks now have a ``org.opencontainers.image.description`` annotation
containing the project's summary and description.


Fixed bugs and issues
---------------------

Fixed in Rockcraft 1.10.0
~~~~~~~~~~~~~~~~~~~~~~~~~

- `#831 <https://github.com/canonical/rockcraft/pull/831>`_ Add missing binaries for the
  ``go-framework`` extension when using bare bases.
- `#839 <https://github.com/canonical/rockcraft/pull/839>`_ Fix Python Chisel slice for
  the ``django-framework`` and ``flask-framework`` extensions when using bare bases.


Contributors
------------

We would like to express a big thank you to all the people who contributed to
this release.

:literalref:`@alesancor1 <https://github.com/alesancor1>`,
:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@cjdcordeiro <https://github.com/cjdcordeiro>`,
:literalref:`@erinecon <https://github.com/erinecon>`,
:literalref:`@jdkandersson <https://github.com/jdkandersson>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@mr-cal <https://github.com/mr-cal>`,
:literalref:`@tigarmo <https://github.com/tigarmo>`,
and :literalref:`@yanksyoon <https://github.com/yanksyoon>`.
