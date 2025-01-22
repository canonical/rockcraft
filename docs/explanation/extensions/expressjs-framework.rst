.. _expressjs-framework-explanation:

expressjs-framework
===================

When using the expressjs-framework extension, there are four different cases for
customizing the Ubuntu base and the Node version to be included.
The main difference is
- whether the bare base is used or the Ubuntu 24.04 base is used.
- whether the Node is installed from Ubuntu packages or the NPM plugin.

Ubuntu base and Node combinations
---------------------------------

Bare base and Node from Ubuntu packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    base: bare
    build-base: ubuntu@24.04
    parts:
        expressjs-framework/install-app:
            plugin: npm
            npm-include-node: false
            build-packages:
            - nodejs
            - npm
            stage-packages:
            - bash_bins
            - coreutils_bins
            - nodejs_bins
        expressjs-framework/runtime:
            plugin: nil
            stage-packages:
            - npm

In this case, the ``npm`` package is installed in a separate ``expressjs-framework/runtime`` part.
This is due to ``expressjs-framework/install-app > stage-packages`` part only being able to install
slices rather than packages as a design choice of Rockcraft. See the comment
https://github.com/canonical/rockcraft/issues/785#issuecomment-2572990545 for more explanation.

Bare base and Node from NPM plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    base: bare
    build-base: ubuntu@24.04
    parts:
        expressjs-framework/install-app:
            plugin: npm
            npm-include-node: true
            npm-node-version: 20.12
            stage-packages:
            - bash_bins
            - coreutils_bins
            - nodejs_bins

In this case, the ``expressjs-framework/install-app > build-packages`` part is empty. The
application is is installed using Node and NPM installed by the NPM plugin. The application is run
using the NPM installed by the NPM plugin.

24.04 base and Node from Ubuntu packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    base: ubuntu@24.04
    parts:
        expressjs-framework/install-app:
            plugin: npm
            npm-include-node: false
            build-packages:
            - nodejs
            - npm
            stage-packages:
            - nodejs_bins
        expressjs-framework/runtime:
            plugin: nil
            stage-packages:
            - npm

In this case, the ``expressjs-framework/install-app > stage-packages`` part does not include the
``bash_bins`` and ``coreutils_bins`` slices as they are already included in the Ubuntu 24.04 base.
The application is built and installed using Node and NPM from the Ubuntu packages.

24.04 base and Node from NPM plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    base: ubuntu@24.04
    parts:
        expressjs-framework/install-app:
            plugin: npm
            npm-include-node: true
            npm-node-version: 20.12

In this case, the application is installed and run via Node and NPM installed by the NPM plugin.
