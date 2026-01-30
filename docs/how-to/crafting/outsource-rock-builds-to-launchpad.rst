.. _how-to-outsource-rock-builds-to-launchpad:

Outsource rock builds to Launchpad
==================================

This guide shows you how to outsource rock builds to the Launchpad `build farm
<https://launchpad.net/builders>`_. By building remotely, you can concurrently
assemble rocks for all supported architectures.

.. important::

    The ``remote-build`` command is experimental and therefore subject to
    change.


Get ready
---------

To build remotely, you will need to:

#. :ref:`sign-up-for-a-launchpad-account`
#. :ref:`define-desired-architectures`
#. :ref:`ensure-project-is-version-controlled-by-git`


.. _sign-up-for-a-launchpad-account:

Sign up for a Launchpad account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build remotely, you need a `Launchpad <https://launchpad.net>`_ account.

If you don't already have an account, you can sign up `here
<https://login.launchpad.net>`_.


.. _define-desired-architectures:

Define desired architectures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you :ref:`start your remote build <start-a-remote-build>`, all architectures
defined in the :ref:`Project.platforms` key of your project file will be built.
Rockcraft currently supports AMD64, ARM64, ARM hard float, IA-32, little-endian PowerPC
64-bit, RISC-V 64-bit and S390x. Your project file can contain any subset of these
architectures.

For example, if you need to build rocks for AMD64, ARM64 and RISC-V 64-bit
architectures, your project file would declare:

.. code-block:: yaml
    :caption: rockcraft.yaml

    platforms:
      amd64:
      arm64:
      riscv64:


.. _ensure-project-is-version-controlled-by-git:

Ensure project is version-controlled by Git
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To start a remote build on Launchpad, your project must be version-controlled by
Git. Note that the repository doesn't need to be hosted on Launchpad prior to
build, as Rockcraft will automatically upload the Git repository in the current
working directory to Launchpad on your behalf.


.. _start-a-remote-build:

Start a remote build
--------------------

In the root directory of your project, begin a remote build with:

.. code-block:: bash

    rockcraft remote-build

When you enter the above command, Rockcraft will ask you to acknowledge that all
remote builds are publicly available on Launchpad.

.. terminal::
    :input: rockcraft remote-build
    :user: ubuntu
    :host: rock-dev

    remote-build is experimental and is subject to change. Use with caution.
    All data sent to remote builders will be publicly available. Are you sure you
    want to continue? [y/N]:

If you aren't logged in or haven't yet :ref:`registered for Launchpad
<sign-up-for-a-launchpad-account>`, Rockcraft will ask you to do so in your web
browser. If this is your first time initiating a remote build from your current
host, you will then be asked to authorize access to your Launchpad account.

Once authorized, your project is uploaded to Launchpad and placed in the build
queues for each architecture defined in your project file. Unless interrupted or
timed out, the status of each build will be continuously monitored and reported
back to you.

If you wish to stop monitoring the build at any time, you can :ref:`interrupt it
<interrupt-a-build>`.


Check the build results
-----------------------

Once all of your builds have either built successfully or failed, your rocks are
downloaded to the root of your project along with their build logs.

Your completed build can also be viewed on Launchpad by going to:

.. code-block:: text

    https://code.launchpad.net/~<user>/<user>-craft-remote-build/+git/<build-id>

Replace ``<user>`` with your Launchpad username and ``<build-id>`` with the ID
displayed when you started your build.


.. _interrupt-a-build:

Interrupt a build
-----------------

Due to build queue lengths varying per architecture, you may want to append the
``--launchpad-timeout=<seconds>`` option to ``remote-build`` to stop monitoring
the build locally after a certain amount of time has elapsed.

If a build is in progress, it can also be interrupted using :kbd:`Ctrl` +
:kbd:`C`, which will give you the option to cancel the build and perform
cleanup. If cancelled, you will not have the option to :ref:`recover this build
later <recover-interrupted-builds>`.

.. _recover-interrupted-builds:


Recover interrupted builds
--------------------------

To resume a build that was interrupted or timed out, navigate to the root of
your project and run:

.. code-block:: bash

    rockcraft remote-build --recover
