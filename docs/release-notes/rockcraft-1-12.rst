.. _release-1.12:

Rockcraft 1.12 release notes
============================

2 June 2025

Learn about the new features, changes, and fixes introduced in Rockcraft 1.12.
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

Rockcraft 1.12 brings the following features, integrations, and improvements.

Spring Boot extension
~~~~~~~~~~~~~~~~~~~~~

The new Spring Boot extension streamlines the process of building rocks that bundle
Spring Boot projects, using either Maven or Gradle as the build tool.

This new extension is experimental and subject to change. For more information, check
out the Spring Boot :ref:`tutorial <tutorial-build-a-rock-for-a-spring-boot-app>` and
:ref:`reference <reference-spring-boot-framework>`.


Minor features
--------------

Rockcraft 1.12 brings the following minor changes.

Support for non-root rocks in 12-factor extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can now set :ref:`Project.run_user` to ``_daemon_`` with extensions that support the
:ref:`12-factor web app <set-up-web-app-rock>` methodology.

12-factor web app documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We added two new how-to guides that cover rocks for 12-factor web apps:

- :ref:`set-up-web-app-rock`
- :ref:`use-web-app-rock`

``mediaType`` field in the OCI manifest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rockcraft now sets the ``mediaType`` field in the image manifest of the generated rocks.
While this field is optional, setting it lets OCI-compliant tools like Bazel's
`rules-oci`_ identify that the manifest is for an OCI image.

Improved ``test`` command
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``CRAFT_ARTIFACT`` environment variable can now be used in tests and contains the
full path to the rock file being tested.

Additionally, the user experience of the ``test`` command has been cleaned up and
improved.

Contributors
------------

We would like to express a big thank you to all the people who contributed to
this release.

:literalref:`@alithethird <https://github.com/alithethird>`,
:literalref:`@erinecon <https://github.com/erinecon>`,
:literalref:`@medubelko <https://github.com/medubelko>`,
:literalref:`@tigarmo <https://github.com/tigarmo>`,
:literalref:`@yanksyoon <https://github.com/yanksyoon>`,
and :literalref:`@zhijie-yang <https://github.com/zhijie-yang>`.


.. _rules-oci: https://github.com/bazel-contrib/rules_oci
