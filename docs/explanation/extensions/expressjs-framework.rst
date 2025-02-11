.. _expressjs-framework-explanation:

expressjs-framework
===================

When using the ``expressjs-framework`` extension, there are four different cases
for customising the Ubuntu base and the Node version to be included.
The main differences are

* whether the bare base is used or the Ubuntu 24.04 base is used.
* whether the Node is installed from Ubuntu packages or the NPM plugin.

Ubuntu base and Node combinations
---------------------------------

In this section of the document, we will discuss the possible combinations of
Ubuntu bases and possible usages of NPM plugin.

24.04 base and Node from Ubuntu packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example uses the Ubuntu 24.04 base and Node from Ubuntu packages.

.. code-block:: yaml

    base: ubuntu@24.04
    extensions:
    - expressjs-framework

In this case, the application is installed and run via Node and NPM is installed
by the Ubuntu packages. The NPM and Node versions are determined by the versions
of NPM and NodeJS shipped with the Ubuntu base. See the NodeJS version shipped
with the corressponding Ubuntu base from the chilsel-slices repository. This
`link to the slices repository <https://github.com/canonical/chisel-releases/\
blob/ubuntu-24.04/slices/nodejs.yaml>`_ is an example of the NodeJS version
shipped with the Ubuntu 24.04 base.

24.04 base and Node from NPM plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example uses the Ubuntu 24.04 base and Node from the NPM plugin.

.. code-block:: yaml

    base: ubuntu@24.04
    extensions:
    - expressjs-framework
    parts:
        expressjs-framework/install-app:
            npm-include-node: true
            npm-node-version: 20.12

In this case, the application is installed and run via Node, and NPM is
installed by the NPM plugin.

Bare base and Node from Ubuntu packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example uses the bare base and Node from Ubuntu packages.

.. code-block:: yaml

    base: bare
    build-base: ubuntu@24.04

In this case, the application is installed and run via Node and NPM is
installed by the Ubuntu packages. The NPM and Node versions are determined by
the versions of NPM and NodeJS shipped with the Ubuntu base.
See the NodeJS version shipped with
the corressponding Ubuntu base from the chilsel-slices repository. This
`link to the slices repository <https://github.com/canonical/chisel-releases/\
blob/ubuntu-24.04/slices/nodejs.yaml>`_ is an example of the NodeJS version
shipped with the Ubuntu 24.04 base.
See the NPM version shipped with the corressponding Ubuntu base from the Ubuntu
packages archive from the `Ubuntu packages search <https://packages.ubuntu.com/\
search?suite=default&section=all&arch=any&keywords=npm&searchon=names>`_.

Bare base and Node from NPM plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example uses the bare base and Node from the NPM plugin.

.. code-block:: yaml

    base: bare
    build-base: ubuntu@24.04
    parts:
        expressjs-framework/install-app:
            npm-include-node: true
            npm-node-version: 20.12

In this case, the application is installed and run via Node and NPM is installed
by the NPM plugin. For different possible inputs for npm-node-version, refer to
the `NPM plugin documentation <https://documentation.ubuntu.com/rockcraft/en/\
latest/common/craft-parts/reference/plugins/npm_plugin>`_.
