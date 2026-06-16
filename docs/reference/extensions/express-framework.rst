.. _reference-express-framework:

Express framework
=================

The Express extension streamlines the process of building Express
application rocks.

It facilitates the installation of Express application dependencies, including
Node.js and npm, inside the rock. Additionally, it transfers your project files
to ``/app`` within the rock.

The Express extension is compatible with the ``bare`` and ``ubuntu@24.04``
:ref:`bases <explanation-bases>`.

.. _reference-express-framework-project-requirements:

Project requirements
--------------------

There are 3 requirements to be able to use the ``expressjs-framework``
extension:

1. The application should reside in the ``app`` directory.
2. The application should have a ``package.json`` file.
3. The ``package.json`` file should define the ``start`` script.
   For more information, see the `npm documentation <https://docs.npmjs.com/cli/v11/configuring-npm/package-json>`_.

.. _reference-express-framework-npm-include-node:

Specifying the Node.js version
------------------------------

You can use the ``npm-include-node`` and ``npm-node-version`` keys to
specify the version of Node.js to be installed. For example:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    expressjs-framework/install-app:
      npm-include-node: true
      npm-node-version: 20.12.2

For more examples of the ``npm-node-version`` key, see
:ref:`craft_parts_npm_plugin`.

If you don't customise the version of node, it will be installed from the Ubuntu
package repository.

.. _reference-express-framework-stage-packages:

Including runtime packages
--------------------------

Installing additional runtime packages is currently unsupported.


Useful links
------------

:ref:`tutorial-build-a-rock-for-an-express-app`
