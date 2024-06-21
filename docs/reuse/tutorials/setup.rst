We recommend starting from a clean Ubuntu 22.04 installation. If you don't have
one available, you can create one using `Multipass`_:

.. collapse:: How to create an Ubuntu 22.04 VM with Multipass

    Is Multipass_ already installed and active? Check by running

    .. code-block:: bash

        sudo snap services multipass

    If you see the ``multipass`` service but it isn't "active", then you'll
    need to run ``sudo snap start multipass``. On the other hand, if you get
    an error saying ``snap "multipass" not found``, then you must install
    `Multipass <install-multipass_>`_:

    .. code-block:: bash

        sudo snap install multipass

    Then you can create the VM with the following command:

    .. code-block:: text

        multipass launch --disk 10G --name rock-dev 22.04

    Finally, once the VM is up, open a shell into it:

    .. code-block:: bash

        multipass shell rock-dev

----

`LXD`_ will be required for building the rock. Make sure it is installed
and initialised:

.. code-block:: bash

   sudo snap install lxd
   lxd init --auto

In order to create the rock, you'll need to install Rockcraft:

.. literalinclude:: /reuse/tutorials/code/task.yaml
    :language: bash
    :start-after: [docs:install-rockcraft]
    :end-before: [docs:install-rockcraft-end]
    :dedent: 2

We'll use Docker to run the rock. You can install it as a ``snap``:

.. literalinclude:: /reuse/tutorials/code/task.yaml
    :language: bash
    :start-after: [docs:install-docker]
    :end-before: [docs:install-docker-end]
    :dedent: 2

.. warning::
   There is a `known connectivity issue with LXD and Docker
   <lxd-docker-connectivity-issue_>`_. If you see a
   networking issue such as "*A network related operation failed in a context
   of no network access*", make sure you apply one of the fixes suggested
   `here <lxd-docker-connectivity-issue_>`_.

Note that you'll also need a text editor. You can either install one of your
choice or simply use one of the already existing editors in your Ubuntu
environment (like ``vi``).

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/how-to-install-multipass
