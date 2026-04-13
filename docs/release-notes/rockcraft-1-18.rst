.. meta::
    :description: Learn about notable features, fixes and documentation updates in Rockcraft 1.18.

.. _release-1.18:

Rockcraft 1.18 release notes
============================

13 April 2026

Learn about the new features, changes, and fixes introduced in Rockcraft 1.18.
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

Rockcraft 1.18 brings the following features, integrations, and improvements.

Support for Ubuntu Pro-compliant rocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rockcraft 1.18 supports packing rocks containing the extended security maintenance fixes and
regulatory compliance enabled by Ubuntu Pro. This feature requires a Pro-enabled system and
is further described on :ref:`this page <how-to-pack-a-pro-rock>`.

``override-overlay`` key
~~~~~~~~~~~~~~~~~~~~~~~~

This new part :ref:`key <partspec.override_overlay>` enables the execution of a bash script
directly on the overlay system. This is in contrast to the existing ``overlay-script`` key
which runs commands on the build system and requires explicit targeting of the overlay.

New .NET plugin
~~~~~~~~~~~~~~~

Rockcraft projects targeting bases ubuntu\@25.10 and higher can now use a new version of the
.NET plugin which provides better control over the distinct steps of a .NET build process.
See the plugin’s :ref:`reference <craft_parts_dotnet_v2_plugin>` for a list of the new keys
and a description of the plugin's behavior.

Updated documentation system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The documentation base is updated to Canonical's Sphinx Starter Pack 1.4.0. Going
forward, the system will stay in step with the Starter Pack, keeping pace with its
features.

The documentation commands that are standard in Canonical products are accessible by
prefixing them with ``docs-``:

.. list-table::
    :header-rows: 1
    :widths: 1 4

    * - Command
      - Result
    * - ``make docs``
      - Renders the docs as a static set of HTML pages.
    * - ``make docs-auto``
      - Hosts the docs in a local server you can view in the web browser. When you save
        a change to a source file, the server updates the doc in real time.
    * - ``make docs-lint``
      - Checks for problems in the documentation.
    * - ``make docs-clean``
      - Removes the built docs and temporary files.
    * - ``make docs-help``
      - See the full list of commands from the Starter Pack.

The Starter Pack is no longer a Git submodule. If you've written for Snapcraft 8 or
lower, or built the documentation before, you must remove the submodule from your host to
continue developing:

.. code-block:: bash

    git submodule deinit -f docs/sphinx-docs-starter-pack
    rm -r docs/sphinx-docs-starter-pack


Minor features
--------------

Rockcraft 1.18 brings the following minor changes.

Better OCI image history
~~~~~~~~~~~~~~~~~~~~~~~~

The rocks packed by Rockcraft now have a description of the commands used to create and
configure each layer.

How-to: migrate to ubuntu\@26.04
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A :ref:`new guide <how-to-migrate-2604>` describes the guidelines for migrating an existing
Rockcraft project to ubuntu\@25.10 and ubuntu\@26.04.


Documentation improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~

We’ve made improvements to the documentation:

- Added expected completion times to the tutorials.
- Updated the Node.js tutorial to display application logs.
- Clarified the UTC timezone on the 12-factor app tutorials.


Fixed bugs and issues
---------------------

The following issues have been resolved in Rockcraft 1.18.


Rockcraft 1.18.0
~~~~~~~~~~~~~~~~

- `#1099 <https://github.com/canonical/rockcraft/pull/1099>`__: fix(oci): ensure config has arch variant
- `#1122 <https://github.com/canonical/rockcraft/pull/1122>`__: fix(docs): add copy button to code blocks
- `#1139 <https://github.com/canonical/rockcraft/pull/1139>`__: fix(docs): Update Spring Boot tutorial

Contributors
------------

We would like to express a big thank you to all the people who contributed to this release.

:literalref:`@Aeonoi <https://github.com/Aeonoi>`,
:literalref:`@alithethird <https://github.com/alithethird>`,
:literalref:`@arturo-seijas <https://github.com/arturo-seijas>`,
:literalref:`@asanvaq <https://github.com/asanvaq>`,
:literalref:`@atandrewlee <https://github.com/atandrewlee>`,
:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@canon-cat <https://github.com/canon-cat>`,
:literalref:`@clay-lake <https://github.com/clay-lake>`,
:literalref:`@EddyPronk <https://github.com/EddyPronk>`,
:literalref:`@erinecon <https://github.com/erinecon>`,
:literalref:`@f-atwi <https://github.com/f-atwi>`,
:literalref:`@FinnRG <https://github.com/FinnRG>`,
:literalref:`@gcomneno <https://github.com/gcomneno>`,
:literalref:`@HamdaanAliQuatil <https://github.com/HamdaanAliQuatil>`,
:literalref:`@javierdelapuente <https://github.com/javierdelapuente>`,
:literalref:`@lengau <https://github.com/lengau>`,
:literalref:`@mateusrodrigues <https://github.com/mateusrodrigues>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@mr-cal <https://github.com/mr-cal>`,
:literalref:`@PraaneshSelvaraj <https://github.com/PraaneshSelvaraj>`,
:literalref:`@smethnani <https://github.com/smethnani>`,
:literalref:`@steinbro <https://github.com/steinbro>`,
:literalref:`@tigarmo <https://github.com/tigarmo>`,
and :literalref:`@zhijie-yang <https://github.com/zhijie-yang>`
