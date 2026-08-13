.. meta::
    :description: Reference documentation for the Express framework extension, which configures Express in a rock and installs Node.js and the app's dependencies.

.. _reference-express-framework:

Express framework
=================

The Express extension streamlines the process of building Express
application rocks.

It facilitates the installation of Express application dependencies, including
Node.js and npm, inside the rock. The extension discovers the location of the
``package.json``, but can only package a single application. If the application
defines a ``build`` script, development dependencies will be installed,
``npm run build`` will be called, and entries matching ``file`` array (excluding
entries from ``.npmignore``, if they exist) will be packages. If the ``files``
array is not defined and ``.npmignore`` does not exist, only files from
the ``dist/`` directory will be packaged.

By default, the system foundation, or base, is set as ``bare`` to generate a
lightweight image.
The Express extension is compatible with the ``bare`` and ``ubuntu@24.04``
bases.

.. _reference-express-framework-project-requirements:

Project requirements
--------------------

There are two requirements to be able to use the ``expressjs-framework``
extension:

1. The application should have a ``package.json`` file.
2. The ``package.json`` file should define the ``start`` script.
   For more information, see the `npm documentation <https://docs.npmjs.com/cli/v11/configuring-npm/package-json>`_.

If the application defines a ``build`` script in ``package.json`` file, it is
recommended to have a ``files`` array describing the entries to be included
or have an appropriate ``.npmignore`` file to exclude entries not required
at runtime. If the ``files`` array is not defined and ``.npmignore``
does not exist, only the ``dist/`` directory will be packaged.

.. _reference-express-framework-npm-include-node:

Node.js version
---------------

The ``npm-include-node`` and ``npm-node-version`` keys
specify the version of Node.js to be installed. For example:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    expressjs-framework/install-app:
      npm-include-node: true
      npm-node-version: 20.12.2

For more examples of the ``npm-node-version`` key, see
:ref:`craft_parts_npm_plugin`.

If you don't customize the version of node, it will be installed from the Ubuntu
package repository.

.. _reference-express-framework-stage-packages:

Additional runtime packages
---------------------------

Installing additional runtime packages is currently unsupported.


Useful links
------------

:ref:`tutorial-build-a-rock-for-an-express-app`
