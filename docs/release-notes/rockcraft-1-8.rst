.. _release-1.8.0:
.. _release-1.8:

Rockcraft 1.8 release notes
===========================

31 January 2025

Learn about the new features, changes, and fixes introduced in Rockcraft 1.8.
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

Rockcraft 1.8 brings the following features, integrations, and improvements.

Improved error reporting
~~~~~~~~~~~~~~~~~~~~~~~~

We improved the reporting of build-time errors to emphasize the precise cause
of the error. For example, here's the output of ``rockcraft build`` when trying
to compile curl with incorrect build options:

.. terminal::

    Failed to run the build script for part 'curl'.
    Detailed information:
    :: + ./configure
    :: configure: error: select TLS backend(s) or disable TLS with --without-ssl.
    :: Select from these:
    ::   --with-amissl
    ::   --with-bearssl
    ::   --with-gnutls
    ::   --with-mbedtls
    ::   --with-openssl (also works for BoringSSL and LibreSSL)
    ::   --with-rustls
    ::   --with-schannel
    ::   --with-secure-transport
    ::   --with-wolfssl
    ...

uv plugin
~~~~~~~~~

We added a plugin to build Python projects that use `uv`_, a performant package
and project manager. See the :ref:`craft_parts_uv_plugin` reference
for details.

JLink plugin
~~~~~~~~~~~~

We added a plugin that uses the `jlink`_ tool to create smaller, optimized
Java runtimes specific for your rock's JARs. See the
:ref:`craft_parts_jlink_plugin` reference for details.

Bash completion
~~~~~~~~~~~~~~~

We added a completion file to the Rockcraft snap, which provides command-line
completion of commands and options in Bash-compatible shells. Try it out by
typing ``rockcraft`` and pressing :kbd:`Tab` in your terminal.


Remote build how-to guide
~~~~~~~~~~~~~~~~~~~~~~~~~

We published :ref:`how-to-outsource-rock-builds-to-launchpad`, a how-to guide for remote
rock builds.


Contributors
------------

We would like to express a big thank you to all the people who contributed to
this release.

:literalref:`@benhoyt<https://github.com/benhoyt>`,
:literalref:`@bepri<https://github.com/bepri>`,
:literalref:`@jahn-junior<https://github.com/jahn-junior>`,
:literalref:`@tigarmo<https://github.com/tigarmo>`.
and :literalref:`@vpa1977<https://github.com/vpa1977>`.

.. _jlink: https://docs.oracle.com/en/java/javase/21/docs/specs/man/jlink.html
.. _uv: https://docs.astral.sh/uv/
