.. meta::
    :description: How to configure the build base for a rock of a 12-factor Express app.

.. _configure-the-build-base-for-an-express-app:

Configure the build base for an Express app
===========================================

When using the ``expressjs-framework`` extension, there are different cases
for customising the Ubuntu base and the Node.js version to be included.
The main differences between the cases are:

- Whether to use the bare base or an Ubuntu base.
- Whether Node.js is installed from Ubuntu package archive or the npm plugin.

The remainder of this page discusses the combinations of
Ubuntu bases and sources for Node.js. Support for Ubuntu 26.04 is experimental.

.. note::
    Part names added by the extension vary by Ubuntu version. On Ubuntu 24.04,
    write ``extension/part``; on Ubuntu 26.04 and higher, write
    ``extension.part``. For rocks with ``base: bare``, follow the convention
    for the configured ``build-base``.

Ubuntu base, Node.js from Ubuntu package archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tab-set::

    .. tab-item:: Ubuntu 24.04
        :sync: base-24

        .. code-block:: yaml
            :caption: rockcraft.yaml

            base: ubuntu@24.04
            extensions:
                - expressjs-framework

    .. tab-item:: Ubuntu 26.04 and higher
        :sync: base-26-plus

        .. code-block:: yaml
            :caption: rockcraft.yaml

            base: ubuntu@26.04
            extensions:
                - expressjs-framework

In this case, the npm plugin copies the app's files and installs its
dependencies. Node.js then provides a runtime and launches the app. The npm and
Node.js versions are determined by the versions shipped with the Ubuntu base.
For example, the `Ubuntu archive
<https://packages.ubuntu.com/noble/npm>`_ lists the npm version shipped with
Ubuntu 24.04.

Ubuntu base, Node.js from npm plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tab-set::

    .. tab-item:: Ubuntu 24.04
        :sync: base-24

        .. code-block:: yaml
            :caption: rockcraft.yaml

            base: ubuntu@24.04
            extensions:
                - expressjs-framework
            parts:
                expressjs-framework/install-app:
                    npm-include-node: true
                    npm-node-version: 20.12

    .. tab-item:: Ubuntu 26.04 and higher
        :sync: base-26-plus

        .. code-block:: yaml
            :caption: rockcraft.yaml

            base: ubuntu@26.04
            extensions:
                - expressjs-framework
            parts:
                expressjs-framework.install-app:
                    npm-include-node: true
                    npm-node-version: 20.12

In this case, the npm plugin copies the app's files and installs its
dependencies. Node.js and npm are installed by the npm plugin.

Bare base, Node.js from Ubuntu package archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tab-set::

    .. tab-item:: Ubuntu 24.04
        :sync: base-24

        .. code-block:: yaml
            :caption: rockcraft.yaml

            base: bare
            build-base: ubuntu@24.04
            extensions:
                - expressjs-framework

    .. tab-item:: Ubuntu 26.04 and higher
        :sync: base-26-plus

        .. code-block:: yaml
            :caption: rockcraft.yaml

            base: bare
            build-base: ubuntu@26.04
            extensions:
                - expressjs-framework

In this case, the npm plugin copies the app's files and installs its
dependencies. Node.js then provides a runtime and launches the app. The npm and
Node.js versions are determined by the versions shipped with the Ubuntu build
base.

Bare base, Node.js from npm plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tab-set::

    .. tab-item:: Ubuntu 24.04
        :sync: base-24

        .. code-block:: yaml
            :caption: rockcraft.yaml

            base: bare
            build-base: ubuntu@24.04
            extensions:
                - expressjs-framework
            parts:
                expressjs-framework/install-app:
                    npm-include-node: true
                    npm-node-version: 20.12

    .. tab-item:: Ubuntu 26.04 and higher
        :sync: base-26-plus

        .. code-block:: yaml
            :caption: rockcraft.yaml

            base: bare
            build-base: ubuntu@26.04
            extensions:
                - expressjs-framework
            parts:
                expressjs-framework.install-app:
                    npm-include-node: true
                    npm-node-version: 20.12

In this case, the npm plugin copies the app's files and installs its
dependencies. Node.js and npm are installed by the npm plugin. For different
possible values for the ``npm-node-version`` key, refer to
:ref:`npm plugin documentation <craft_parts_npm_plugin>`.
