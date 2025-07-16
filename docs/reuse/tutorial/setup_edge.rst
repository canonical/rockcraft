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

In order to create the rock, we'll install Rockcraft with
classic confinement, which grants it access to the whole file system:

.. literalinclude:: /reuse/tutorial/code/edge/task.yaml
    :language: bash
    :start-after: [docs:install-rockcraft]
    :end-before: [docs:install-rockcraft-end]
    :dedent: 2

This tutorial requires the ``latest/edge`` channel of Rockcraft as the
framework is currently experimental.

We'll use Docker to run the rock. We can install it as a ``snap``:

.. literalinclude:: /reuse/tutorial/code/edge/task.yaml
    :language: bash
    :start-after: [docs:install-docker]
    :end-before: [docs:install-docker-end]
    :dedent: 2

By default, Docker is only accessible with root privileges (``sudo``). We want
to be able to use Docker commands as a regular user:

.. literalinclude:: /reuse/tutorial/code/edge/task.yaml
    :language: bash
    :start-after: [docs:docker-regular-user]
    :end-before: [docs:docker-regular-user-end]
    :dedent: 2

Restart Docker:

.. literalinclude:: /reuse/tutorial/code/stable/task.yaml
    :language: bash
    :start-after: [docs:docker-enable]
    :end-before: [docs:docker-enable-end]
    :dedent: 2

Note that we'll also need a text editor. We can either install one of our
choice or simply use one of the already existing editors in the Ubuntu
environment (like ``vi``).

.. _`install-multipass`: https://multipass.run/docs/install-multipass
