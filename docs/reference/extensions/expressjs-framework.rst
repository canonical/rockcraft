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

There is 1 requirement to be able to use the ``expressjs-framework`` extension:

1. There must be a ``package.json`` file in the ``app`` directory of the project
    with ``start`` script defined.

``parts`` > ``expressjs-framework/dependencies:`` > ``stage-packages``
======================================================================

You can use this key to specify any dependencies required for your ExpressJS
application. In the following example we use it to specify ``libpq-dev``:

.. code-block:: yaml

  parts:
    expressjs-framework/dependencies:
      stage-packages:
        # list required packages or slices for your ExpressJS application below.
        - libpq-dev


``parts`` > ``expressjs-framework/install-app`` > ``prime``
===========================================================

You can use this field to specify the files to be included or excluded from
your rock upon ``rockcraft pack``. Follow the ``app/<filename>`` notation. For
example:

.. code-block:: yaml

  parts:
    expressjs-framework/install-app:
      prime:
        - app/.env
        - app/script.js
        - app/templates
        - app/static

Some files/directories, if they exist, are included by default. These include:
``<rock name>``, ``app.js``, ``migrate``, ``migrate.sh``, ``migrate.py``,
``bin``, ``public``, ``routes``, ``views``, ``package.json``,
``package-lock.json``.

Useful links
============

- :ref:`build-a-rock-for-an-expressjs-application`
