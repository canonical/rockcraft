.. _release-1.13:

Rockcraft 1.13 release notes
============================

11 July 2025

Learn about the new features, changes, and fixes introduced in Rockcraft 1.13.
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

Rockcraft 1.13 brings the following features, integrations, and improvements.

.NET plugin (v2)
~~~~~~~~~~~~~~~~

The :ref:`craft_parts_dotnet_v2_plugin` is now available. It's a new version
of the plugin that's easier to use and configure.

Minor features
--------------

Rockcraft 1.13 brings the following minor changes.

Improved ``test`` command
~~~~~~~~~~~~~~~~~~~~~~~~~

You can now select which tests to run in the ``test`` command by passing a selector.
Selection takes this form:

.. code-block:: bash

    rockcraft test <selector> --debug

The `spread documentation`_ details the selector syntax.

Improved documentation for 12-factor app extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tutorial and reference pages for all 12-factor app extensions were improved
based on user feedback, with fixes to multiple steps that were showstoppers.

We also added information about using the `StatsD`_
exporter to the references for the :ref:`reference-django-framework` and
:ref:`reference-flask-framework` extensions.

Contributors
------------

We would like to express a big thank you to all the people who contributed to
this release.

:literalref:`@AlexBaranowski <https://github.com/AlexBaranowski>`,
:literalref:`@bepri <https://github.com/bepri>`,
:literalref:`@erinecon <https://github.com/erinecon>`,
:literalref:`@jahn-junior <https://github.com/jahn-junior>`,
:literalref:`@javierdelapuente <https://github.com/javierdelapuente>`,
:literalref:`@lengau <https://github.com/lengau>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@sergiusens <https://github.com/sergiusens>`,
and :literalref:`@tigarmo <https://github.com/tigarmo>`.


.. _StatsD: https://github.com/statsd/statsd
.. _spread documentation: https://github.com/canonical/spread#selecting-which-tasks-to-run
