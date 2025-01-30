.. _outsource-rock-builds-to-launchpad:


Outsource rock builds to Launchpad
==================================

This guide will show you how to outsource your rock builds to Launchpad's `build
farm <https://launchpad.net/builders>`_ using the ``remote-build`` command. By
building remotely, you will be able to concurrently assemble your rocks
for any of Rockcraft's supported architectures.

.. important::

    The ``remote-build`` command is experimental and therefore subject to
    change.


Sign up for a Launchpad account
-------------------------------

In order to use Rockcraft's ``remote-build`` command, you will need to register
for an account on `Launchpad <https://launchpad.net>`_.

If you do not already have an account, you can sign up `here
<https://login.launchpad.net>`_.


Define desired architectures
----------------------------

Once you `start your remote build <#start-a-remote-build>`_, all architectures
defined in the :ref:`platforms` key of your project file will be built.
Rockcraft currently supports AMD64, ARM64, ARM hard float, IA-32, PowerPC 64-bit
little-endian, RISC-V 64-bit and S390x. Your project file can contain any subset
of these architectures.

For example, if you need to build rocks for AMD64, ARM64 and RISC-V 64-bit
architectures, your project file will include:

.. code-block:: yaml

    platforms:
      amd64:
      arm64:
      riscv64:


Start a remote build
--------------------

To start a remote build on Launchpad, your project must be version-controlled by
Git. Note that the repository doesn't need to be hosted on Launchpad prior to
build, as Rockcraft will automatically upload the Git repository in the current
working directory to Launchpad on your behalf.

In the root directory of your project, you can now begin your remote build with:

.. code-block:: bash

    rockcraft remote-build

Due to build queue lengths varying per architecture, you may want to append the
``--launchpad-timeout=<seconds>`` option to stop monitoring the build locally
after a certain amount of time has elapsed. Once timed out on your local
machine, the build will continue on Launchpad and can be `recovered
<#recover-interrupted-builds>`_ at any point.

At this point, you will be asked to acknowledge that all remote builds are
publicly available on Launchpad.

.. terminal::
    :input: rockcraft remote-build
    :user: ubuntu
    :host: rock-dev

    remote-build is experimental and is subject to change. Use with caution.
    All data sent to remote builders will be publicly available. Are you sure you
    want to continue? [y/N]:

If you are not logged in or have not yet `registered for Launchpad
<#sign-up-for-a-launchpad-account>`_, you will now be prompted to do so in your
browser. If this is your first time initiating a remote build from your current
machine, you will then be asked to authorize access to your Launchpad account.

Once authorized, your project will be uploaded to Launchpad and placed in the
build queues for each architecture defined in your project file.
Unless a local timeout was specified, the status of each build will be
continuously monitored and reported back to you.


Check the build results
-----------------------

Once all of your builds have either built successfully or failed, your rocks
will be downloaded to the root of your project along with their build logs.

Your completed build can also be viewed on Launchpad by navigating to:

.. code-block:: text

    https://code.launchpad.net/~<user>/<user>-craft-remote-build/+git/<build-id>

where ``<user>`` is your Launchpad username and ``<build-id>`` is the ID
displayed when you started your build.


Recover interrupted builds
--------------------------

To resume a build that was interrupted or timed out, navigate to the root of
your project and run:

.. code-block:: bash

    rockcraft remote-build --recover
