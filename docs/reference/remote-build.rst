.. _ref-remote-build:


*************
Remote builds
*************

Remote build is a feature in Rockcraft that offloads the build process to
`Launchpad`_'s `build farm`_ to build multiple rocks simultaneously, and for
different architectures than your running machine.


Pre-requisites
--------------

In order to perform remote builds, the following conditions must be met:

- You must have a `Launchpad account`_, as the remote builds are performed on
  Launchpad.
- The Rockcraft project must be version-controlled by Git. This is because
  Rockcraft uses a Git-based workflow to upload the project to Launchpad.
- The repository hosting the Rockcraft project must not be a shallow clone,
  because Git does not support pushing shallow clones.


Overview
--------

Remote builds are launched by running ``rockcraft remote-build``. Rockcraft will
upload the Git repository on the current working directory to Launchpad on your
behalf, under your account. Next, it will trigger builds for the Rockcraft
project present on the root of the repository and continuously monitor the
status of the new builds.

Once all builds are done (either through a successful build or a failure), the
rock files will be downloaded to the current directory, together with the build
logs.


Limitations
-----------

The following is a list of the current limitations of the remote build feature,
which are planned to be addressed in the future:

- The prospective rock must be open source and public, because the remote builds
  will be publicly available.
- All architectures defined on the project's ``platforms`` entry - either
  explicitly via the ``build-on`` key or implicitly through the platform
  shorthand - will be built. There is currently no way to restrict the set of
  platforms to build remotely.


.. _`Launchpad`: https://launchpad.net/
.. _`build farm`: https://launchpad.net/builders
.. _`Launchpad account`: https://launchpad.net/+login
