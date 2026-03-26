.. _release-1.11:

Rockcraft 1.11 release notes
============================

2 May 2025

Learn about the new features, changes, and fixes introduced in Rockcraft 1.11.
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

Rockcraft 1.11 brings the following features, integrations, and improvements.

Test command
~~~~~~~~~~~~

A new command called ``test``, and its accompanying ``init`` profile, are available for
testing rocks. They leverage `Spread`_ to run identically on local and remote systems.

The command is experimental and subject to change. To try it on an existing rock
project, run ``rockcraft init --profile=test`` at the root of your project directory.
For a description of the command and its options, run ``rockcraft test --help``.

Cargo-use plugin
~~~~~~~~~~~~~~~~

We added a plugin that sets up a local `cargo registry`_ for `Rust`_ crates. These
crates can then be used by the existing :ref:`Rust plugin <craft_parts_rust_plugin>`.
See the :ref:`craft_parts_cargo_use_plugin` reference for details.

Gradle plugin
~~~~~~~~~~~~~

We added a plugin to build sources using the `Gradle`_ build tool. See the
:ref:`craft_parts_gradle_plugin` reference for details.

Minor features
--------------

Rockcraft 1.11 brings the following minor changes.

Support for Maven wrappers
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Maven plugin now supports the ``maven-use-wrapper`` key to indicate that the build
should use the wrapper provided by the source code. See the
:ref:`craft_parts_maven_plugin` reference for details.

Contributors
------------

We would like to express a big thank you to all the people who contributed to
this release.

:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@lengau <https://github.com/lengau>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@mr-cal <https://github.com/mr-cal>`,
:literalref:`@sergiusens <https://github.com/sergiusens>`,
and :literalref:`@tigarmo <https://github.com/tigarmo>`.


.. _Gradle: https://gradle.org/
.. _Rust: https://doc.rust-lang.org/stable/
.. _Spread: https://github.com/canonical/spread
.. _cargo registry: https://doc.rust-lang.org/cargo/reference/registries.html
