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
3. The ``package.json`` file should defined the ``start`` script.


``parts`` > ``expressjs-framework/install-app`` > ``npm-include-node``
======================================================================

You can use this field to specify the version of Node to be installed. For
example:

.. code-block:: yaml

  parts:
    expressjs-framework/install-app:
      npm-include-node: true
      npm-node-version: node

A corressponding Ubuntu packaged Node version will be provided by default if
not specified.

``parts`` > ``expressjs-framework/runtime:`` > ``stage-packages``
=================================================================

You can use this key to specify any dependencies required for your ExpressJS
application. In the following example we use it to specify ``libpq-dev``:

.. code-block:: yaml

  parts:
    expressjs-framework/runtime:
      stage-packages:
        # when using the default provided node version, the npm package is
        # required.
        # - npm
        # list required packages or slices for your ExpressJS application below.
        - libpq-dev

Useful links
============

- :ref:`build-a-rock-for-an-expressjs-application`
