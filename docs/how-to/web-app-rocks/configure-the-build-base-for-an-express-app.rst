.. _configure-the-build-base-for-an-express-app:

Configure the build base for an Express app
===========================================

When using the ``expressjs-framework`` extension, there are four different cases
for customising the Ubuntu base and the Node.js version to be included.
The main differences between the cases are:

- Whether to use the bare base or Ubuntu 24.04 base.
- Whether Node.js is installed from Ubuntu package archive or the NPM plugin.

The remainder of this page discusses the combinations of
Ubuntu bases and sources for Node.js.

Ubuntu 24.04 base, Node.js from Ubuntu package archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml
    :caption: rockcraft.yaml

    base: ubuntu@24.04
    extensions:
        - expressjs-framework

In this case, the NPM plugin copies the app's files and installs its
dependencies. Node.js then provides a runtime and launches the app. The NPM and
Node.js versions are determined by the versions of NPM and Node.js shipped with
the Ubuntu base. This `link to the Ubuntu archive
<https://packages.ubuntu.com/noble/npm>`_ shows the NPM version shipped with the
Ubuntu 24.04 base.

Ubuntu 24.04 base, Node.js from NPM plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml
    :caption: rockcraft.yaml

    base: ubuntu@24.04
    extensions:
        - expressjs-framework
    parts:
        expressjs-framework/install-app:
            npm-include-node: true
            npm-node-version: 20.12

In this case, the NPM plugin copies the app's files and installs its
dependencies. Node.js and NPM is installed by the NPM plugin.

Bare base, Node.js from Ubuntu package archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml
    :caption: rockcraft.yaml

    base: bare
    build-base: ubuntu@24.04
    extensions:
        - expressjs-framework

In this case, the NPM plugin copies the app's files and installs its
dependencies. Node.js then provides a runtime and launches the app. The NPM and
Node.js versions are determined by the versions of NPM and Node.js shipped with
the Ubuntu base.

Bare base, Node.js from NPM plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml
    :caption: rockcraft.yaml

    base: bare
    build-base: ubuntu@24.04
    parts:
        expressjs-framework/install-app:
            npm-include-node: true
            npm-node-version: 20.12

In this case, the NPM plugin copies the app's files and installs its
dependencies. Node.js then provides a runtime and launches the app. Node.js and
NPM is installed by the NPM plugin. For different possible values for the
``npm-node-version`` key, refer to
:ref:`NPM plugin documentation <craft_parts_npm_plugin>`.
