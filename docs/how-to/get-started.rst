How to get started - quick guide
********************************

See the :ref:`tutorial` for a full getting started guide.

Getting started
---------------

Rockcraft is **the tool** for building Ubuntu-based and production-grade OCI
images, aka rocks!

Rockcraft is distributed as a snap. For packing new rocks, it makes use of
"providers" to execute all the steps involved in the rock's build process. At
the moment, the supported providers are LXD and Multipass.

Requirements
............

Before installing the Rockcraft snap, make sure you have the necessary tools and
environment to install and run Rockcraft.

First things first, if you are running Ubuntu, Snap is already installed and
ready to go:

.. literalinclude:: code/get-started/task.yaml
    :language: bash
    :start-after: [docs:snap-version]
    :end-before: [docs:snap-version-end]
    :dedent: 2

You'll get something like:

..  code-block:: text
    :emphasize-lines: 1,2
    :class: log-snippets

    snap    2.57.1
    snapd   2.57.1
    series  16
    ubuntu  22.04
    kernel  5.17.0-1016-oem

If this is not the case, then please check
https://snapcraft.io/docs/installing-snap-on-ubuntu.

For what concerns providers, LXD is the default one for Rockcraft, so start by
checking if it is available:

.. literalinclude:: code/get-started/task.yaml
    :language: bash
    :start-after: [docs:lxd-version]
    :end-before: [docs:lxd-version-end]
    :dedent: 2

The output will be something like:

..  code-block:: text
    :class: log-snippets

    5.5

And that it is enabled:

.. literalinclude:: code/get-started/task.yaml
    :language: bash
    :start-after: [docs:lxd-status]
    :end-before: [docs:lxd-status-end]
    :dedent: 2

The output should look like:

..  code-block:: text
    :emphasize-lines: 3
    :class: log-snippets

    ● snap.lxd.daemon.service - Service for snap application lxd.daemon
        Loaded: loaded (/etc/systemd/system/snap.lxd.daemon.service; static)
        Active: active (running) since Wed 2022-09-07 16:02:29 CEST; 6 days ago
        ...

If LXD is not installed, then run:

.. literalinclude:: code/get-started/task.yaml
    :language: bash
    :start-after: [docs:lxd-install]
    :end-before: [docs:lxd-install-end]
    :dedent: 2


And if LXD is not running, try starting it via:

.. literalinclude:: code/get-started/task.yaml
    :language: bash
    :start-after: [docs:lxd-init]
    :end-before: [docs:lxd-init-end]
    :dedent: 2


May you find any problems with LXD, please check https://ubuntu.com/lxd.


Choose a Rockcraft release
..........................

Pick a Rockcraft release, either from the `snap store`_ or via
``snap search rockcraft``.

Keep in mind the chosen channel, as riskier releases are more prone to breaking
changes.

Also, note that the Rockcraft's snap confinement is set to "classic" (this is
important for the installation step).


Installation steps
..................

Having chosen a Rockcraft release, you must now install it via the snap CLI (or
directly via the Ubuntu Desktop store):

.. code-block:: text

    sudo snap install rockcraft --channel=<chosen channel> --classic

For example:

.. literalinclude:: code/get-started/task.yaml
    :language: bash
    :start-after: [docs:install-rockcraft]
    :end-before: [docs:install-rockcraft-end]
    :dedent: 2

.. note::
    Note the use of :code:`--classic` in order for rockcraft to launch LXD
    instances or run in :code:`--destructive` mode.

Rockcraft is packed along other apps like `skopeo`_, `umoci`_ and
`chisel`_. Both Chisel and Umoci are used internally, while skopeo
is exposed externally and can be used via :code:`rockcraft.skopeo` to
manage the OCI archives.

Testing Rockcraft
.................

Once installed, you can make sure that Rockcraft is actually present in the
system and ready to be used:

.. literalinclude:: code/get-started/task.yaml
    :language: bash
    :start-after: [docs:rockcraft-version]
    :end-before: [docs:rockcraft-version-end]
    :dedent: 2

The output will be similar to:

..  code-block:: text
    :class: log-snippets

    rockcraft 0.0.1.dev1

.. _snap store: https://snapcraft.io/rockcraft
.. _skopeo: https://github.com/containers/skopeo
.. _umoci: https://umo.ci/
