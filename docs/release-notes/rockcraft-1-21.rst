.. meta::
    :description: Release notes for Rockcraft 1.21.

.. _release-1.21:

Rockcraft 1.21 release notes
============================

5 October 2026

Learn about the new features, changes, and fixes introduced in Rockcraft 1.21.
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

Rockcraft 1.21 brings the following features, integrations, and improvements.

Unified version selection with ``@``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to standardize package declarations, Rockcraft now supports the use of the ``@``
character to separate a package name from its version. This notation is supported for
debs (build-packages and stage-packages) and snaps (build-snaps and stage-snaps).

The previous notation to declare package versions is still supported for all supported
bases up to ubuntu\@26.10, but future bases will only support the use of ``@``.

Init Git repositories
~~~~~~~~~~~~~~~~~~~~~

The :ref:`init command <ref_commands_init>` now features a ``--vcs`` option to initialize
a Git repository when creating the Rockcraft project.

stage-slices key
~~~~~~~~~~~~~~~~

Rockcraft 1.21 introduces the ``stage-slices`` key, which specifies a list of Chisel slices
to be cut into the part's install directory. Slices can still be declared in ``stage-packages``,
but this support will be dropped starting with base ubuntu\@27.04.

Support for uv in 12-factor extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Flask, Django, and FastAPI extensions now support Python projects that use uv.

Experimental monorepo support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Support for packing projects where the Rockcraft project file is not on the root of the
repository can now be enabled with the ``ROCKCRAFT_EXPERIMENTAL_MONOREPO`` environment
variable.

This support is experimental and might change in future releases as we
improve the monorepo experience. For guidance, see :ref:`how-to-pack-a-rock-in-a-monorepo`.

Minor features
--------------

Rockcraft 1.21 brings the following minor changes.

Smarter repacking
~~~~~~~~~~~~~~~~~

Rockcraft will now skip re-packing the rock if the project is unchanged.

Sticky bit on Pebble directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``/var/lib/pebble/default/`` directory now respects the sticky bit so that users
can't remove or rename entries made by other users.

Testing with fetch-service sessions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``rockcraft test`` now configures the proxy settings on Spread runners when
``CRAFT_USE_EXTERNAL_FETCH_SERVICE`` is set.

Contributors
------------

We would like to express a big thank you to all the people who contributed to this release.

:literalref:`@0xzoowa <https://github.com/0xzoowa>`,
:literalref:`@aahil-khan <https://github.com/aahil-khan>`,
:literalref:`@alithethird <https://github.com/alithethird>`,
:literalref:`@artivis <https://github.com/artivis>`,
:literalref:`@asanvaq <https://github.com/asanvaq>`,
:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@canon-cat <https://github.com/canon-cat>`,
:literalref:`@cmatsuoka <https://github.com/cmatsuoka>`,
:literalref:`@EdmilsonRodrigues <https://github.com/EdmilsonRodrigues>`,
:literalref:`@erinecon <https://github.com/erinecon>`,
:literalref:`@gcomneno <https://github.com/gcomneno>`,
:literalref:`@HeRaNO <https://github.com/HeRaNO>`,
:literalref:`@Huoyanlifusu <https://github.com/Huoyanlifusu>`,
:literalref:`@jahn-junior <https://github.com/jahn-junior>`,
:literalref:`@javierdelapuente <https://github.com/javierdelapuente>`,
:literalref:`@lengau <https://github.com/lengau>`,
:literalref:`@Marcel-Ramos-byte <https://github.com/Marcel-Ramos-byte>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@mr-cal <https://github.com/mr-cal>`,
:literalref:`@nicolasbock-canonical <https://github.com/nicolasbock-canonical>`,
:literalref:`@smethnani <https://github.com/smethnani>`,
:literalref:`@steinbro <https://github.com/steinbro>`,
:literalref:`@Tejas-Raj01 <https://github.com/Tejas-Raj01>`,
:literalref:`@Thanhphan1147 <https://github.com/Thanhphan1147>`,
:literalref:`@tigarmo <https://github.com/tigarmo>`,
:literalref:`@Turan52 <https://github.com/Turan52>`,
:literalref:`@upils <https://github.com/upils>`,
:literalref:`@vismaytiwari <https://github.com/vismaytiwari>`,
and :literalref:`@zhijie-yang <https://github.com/zhijie-yang>`.
