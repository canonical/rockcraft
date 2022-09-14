*************
How-to guides
*************

If you have a specific goal but are already familiar with Rockcraft, our How-to guides have more in-depth detail than our tutorials 
and can be applied to a broader set of applications. 

They'll help you achieve an end result but may require you to understand and adapt the steps to fit your specific requirements.


Getting started
---------------

Rockcraft is **the tool** for building Ubuntu-based and production-grade OCI images, aka ROCKs!

Rockcraft is distributed as a snap. For packing new ROCKs, it makes use of "providers" to execute 
all the steps involved in the ROCK's build process. At the moment, the supported providers are LXD and Multipass.

Requirements
............

Before installing the Rockcraft snap, make sure you have the necessary tools and environment to 
install and run Rockcraft.

First things first, if you are running Ubuntu, Snap is already installed and ready to go:

.. code-block:: sh

    $ snap --version
    snap    2.57.1
    snapd   2.57.1
    series  16
    ubuntu  22.04
    kernel  5.17.0-1016-oem

If this is not the case, then please check https://snapcraft.io/docs/installing-snap-on-ubuntu.

For what concerns providers, LXD is the default one for Rockcraft, so start by checking if it is available and enabled:

.. code-block:: sh

  $ lxd --version
  5.5
  $ systemctlstatus snap.lxd.daemon.service
  ● snap.lxd.daemon.service - Service for snap application lxd.daemon
      Loaded: loaded (/etc/systemd/system/snap.lxd.daemon.service; static)
      Active: active (running) since Wed 2022-09-07 16:02:29 CEST; 6 days ago
      ...

If LXD is not installed, then run:

.. code-block:: sh

  $ snap install lxd

And if LXD is not running, try starting it via:

.. code-block:: sh

  $ lxd init


May you find any problems with LXD, please check https://ubuntu.com/lxd.

It is also useful to ensure also Multipass is installed and available:

.. code-block:: sh

    $ multipass version
    multipass   1.10.1

If it is not, please check https://multipass.run/docs/installing-on-linux.


Choose a Rockcraft release
..........................

Pick a Rockcraft release, either from the `snap store <https://snapcraft.io/rockcraft>`_ or via 
``snap search rockcraft``. 

Keep in mind the chosen channel, as riskier releases are more prone to breaking changes.

Also, note that the Rockcraft's snap confinement is set to "classic" (this is important for the installation step).


Installation steps
..................

Having chosen a Rockcraft release, you must now install it via the snap CLI (or directly via the Ubuntu Desktop store):

.. code-block:: sh 

    $ sudo snap install rockcraft --channel=<chosen channel> --classic

For example:

.. code-block:: sh 

    $ sudo snap install rockcraft --channel=latest/edge --classic



Testing Rockcraft
.................

Once installed, you can make sure that Rockcraft is actually present in the system and ready to be used:

.. code-block:: sh

    $ rockcraft --version
    rockcraft 0.0.1.dev1                          

