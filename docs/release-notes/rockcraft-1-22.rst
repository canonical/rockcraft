.. meta::
    :description: Release notes for Rockcraft 1.22.

.. _release-1.22:

Rockcraft 1.22 release notes
============================

23 November 2026

Learn about the new features, changes, and fixes introduced in Rockcraft 1.22.
For information about the Rockcraft release cycle, see the
:ref:`release_policy_and_schedule`.


Requirements and compatibility
------------------------------

To run Rockcraft, a system requires the following minimum hardware and
installed software. These requirements apply to local hosts as well as VMs and
container hosts.


Minimum hardware requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- AMD64, ARM64, ARMHF, RISC-V (RVA20), PPC64EL, or S390X-capable
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

Rockcraft 1.22 brings the following features, integrations, and improvements.

Support for ``ubuntu@26.10``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rockcraft now supports building rocks with the ``ubuntu@26.10`` base. If you were already
building experimental ``ubuntu@26.10`` rocks, you can drop ``build-base: devel`` from
your project file.

Fallback to the Azure Container Registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rockcraft will now try to fetch the base Ubuntu image from the Azure Container Registry
(ACR) if the attempt to fetch from the Elastic Container Registry (ECR) fails because of
rate-limiting, which can happen in Continuous Integration environments.

Minor features
--------------

Rockcraft 1.22 brings the following minor changes.

Chisel slices on ``ubuntu@26.10`` rocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rockcraft is now capable of cutting Chisel slices when building ``ubuntu@26.10`` rocks.

Creation timestamp on bare rocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rockcraft will now correctly set a creation timestamp when packing bare-based rocks.

Documentation improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~

We've made improvements to the documentation:

* Expanded the 12-factor extension documentation for Ubuntu 26.04, including the web app
  setup and usage guides, Spring Boot initialization, and Express examples.
  Clarified extension-specific behavior for included files, Go module naming, package
  slices on bare rocks, and Express build outputs.
* Corrected migration guidance and documented npm-node-version values in the Express
  build-base guide.
* Updated the Chisel-related terminology from ``SDF`` to ``package slices file``.
* Added a new explanation page that describes the documentation system, process, and
  writing style and conventions in Rockcraft.
* Updated the guidance on how to update the documentation tooling.

Contributors
------------

We would like to express a big thank you to all the people who contributed to this release.

:literalref:`@alesancor1 <https://github.com/alesancor1>`,
:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@cmatsuoka <https://github.com/cmatsuoka>`,
:literalref:`@cyh2012aa <https://github.com/cyh2012aa>`,
:literalref:`@dangertoaster <https://github.com/dangertoaster>`,
:literalref:`@GreyViperTooth <https://github.com/GreyViperTooth>`,
:literalref:`@jahn-junior <https://github.com/jahn-junior>`,
:literalref:`@lczyk <https://github.com/lczyk>`,
:literalref:`@lengau <https://github.com/lengau>`,
:literalref:`@LoweRAM <https://github.com/LoweRAM>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@mr-cal <https://github.com/mr-cal>`,
:literalref:`@Shahzeb-DataEngineer <https://github.com/Shahzeb-DataEngineer>`,
:literalref:`@smethnani <https://github.com/smethnani>`,
:literalref:`@steinbro <https://github.com/steinbro>`,
and :literalref:`@tigarmo <https://github.com/tigarmo>`.
