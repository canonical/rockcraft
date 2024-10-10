We recommend starting from a clean Ubuntu installation. If we don't have
one available, we can create one using `Multipass`_:

.. tabs::

    .. tab:: Ubuntu

        Is Multipass_ already installed and active? Check by running

        .. code-block:: bash

            snap services multipass

        If we see the ``multipass`` service but it isn't "active", then we'll
        need to run ``sudo snap start multipass``. On the other hand, if we get
        an error saying ``snap "multipass" not found``, then we must install
        `Multipass <install-multipass_>`_:

        .. code-block:: bash

            sudo snap install multipass

    .. tab:: Windows

        See `Multipass installation instructions <install-multipass_>`_, switch
        to Windows in the drop down.

    .. tab:: macOS

        See `Multipass installation instructions <install-multipass_>`_, switch
        to macOS in the drop down.

Then we can create the VM with the following command:

.. code-block:: text

    multipass launch --disk 10G --name rock-dev 24.04

Finally, once the VM is up, open a shell into it:

.. code-block:: bash

    multipass shell rock-dev

----

`LXD`_ will be required for building the rock. Make sure it is installed
and initialised:

.. code-block:: bash

   sudo snap install lxd
   lxd init --auto

In order to create the rock, we'll need to install Rockcraft:

.. literalinclude:: /reuse/tutorial/code/task.yaml
    :language: bash
    :start-after: [docs:install-rockcraft]
    :end-before: [docs:install-rockcraft-end]
    :dedent: 2

We'll use Docker to run the rock. We can install it as a ``snap``:

.. literalinclude:: /reuse/tutorial/code/task.yaml
    :language: bash
    :start-after: [docs:install-docker]
    :end-before: [docs:install-docker-end]
    :dedent: 2

By default, Docker is only accessible with root privileges (``sudo``). We want
to be able to use Docker commands as a regular user:

.. literalinclude:: /reuse/tutorial/code/task.yaml
    :language: bash
    :start-after: [docs:docker-regular-user]
    :end-before: [docs:docker-regular-user-end]
    :dedent: 2

.. warning::
   There is a `known connectivity issue with LXD and Docker
   <lxd-docker-connectivity-issue_>`_. If we see a
   networking issue such as "*A network related operation failed in a context
   of no network access*", make sure to apply one of the suggested fixes
   `here <lxd-docker-connectivity-issue_>`_.

Note that we'll also need a text editor. We can either install one of our
choice or simply use one of the already existing editors in the Ubuntu
environment (like ``vi``).

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/how-to-install-multipass
