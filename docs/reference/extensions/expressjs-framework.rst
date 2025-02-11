.. _expressjs-framework-reference:

expressjs-framework
-------------------

The ExpressJS extension streamlines the process of building ExpressJS
application rocks.

It facilitates the installation of ExpressJS application dependencies, including
Node and NPM, inside the rock. Additionally, it transfers your project files to
``/app`` within the rock.

.. note::
    The ExpressJS extension is compatible with the ``bare`` and ``ubuntu@24.04``
    bases.

Project requirements
====================

There are 3 requirements to be able to use the ``expressjs-framework``
extension:

1. The application should reside in the ``app`` directory.
2. The application should have a ``package.json`` file.
3. The ``package.json`` file should define the ``start`` script.


``parts`` > ``expressjs-framework/install-app`` > ``npm-include-node``
======================================================================

You can use this field to specify the version of Node to be installed. For
example:

.. code-block:: yaml

  parts:
    expressjs-framework/install-app:
      npm-include-node: true
      npm-node-version: 20.12.2

For more examples of npm-node-version options, see: `Rockcraft | NPM Plugin |
Examples <https://documentation.ubuntu.com/rockcraft/en/1.5.3/common/\
craft-parts/reference/plugins/npm_plugin/#examples>`_.

If you don't customise the version of node, it will be installed from the Ubuntu
package repository.

``parts`` > ``expressjs-framework/runtime:`` > ``stage-packages``
=================================================================

Installing additional runtime packages is currently unsupported due to some
limitations of the Rockcraft tool.

Useful links
============

- :ref:`build-a-rock-for-an-expressjs-application`
