.. _fastapi-framework-reference:

fastapi-framework
-----------------

The FastAPI extension streamlines the process of building FastAPI application
rocks.

It facilitates the installation of FastAPI application dependencies, including
Uvicorn, inside the rock. Additionally, it transfers your project files to
``/app`` within the rock.

.. note::
    The FastAPI extension is compatible with the ``bare`` and ``ubuntu@24.04``
    bases.

Project requirements
====================

There are 2 requirements to be able to use the ``fastapi-framework`` extension:

1. There must be a ``requirements.txt`` file in the root of the project with
   ``fastapi`` declared as a dependency
2. The project must include a ASGI app in a variable called ``app`` in one of
   the following files relative to the project root (in order of priority):

   * ``app.py``
   * ``main.py``
   * ``__init__.py``, ``app.py`` or ``main.py`` within the ``app`` or ``src``
     directory or within a directory with the name of the rock as declared in
     ``rockcraft.yaml``.

``parts`` > ``fastapi-framework/dependencies:`` > ``stage-packages``
====================================================================

You can use this key to specify any dependencies required for your FastAPI
application. For example, below we use it to specify ``libpq-dev``:

.. code-block:: yaml

  parts:
    fastapi-framework/dependencies:
      stage-packages:
        # list required packages or slices for your FastAPI application below.
        - libpq-dev


``parts`` > ``fastapi-framework/install-app`` > ``prime``
=========================================================

You can use this field to specify the files to be included or excluded from
your rock upon ``rockcraft pack``. Follow the ``app/<filename>`` notation. For
example:

.. code-block:: yaml

  parts:
    fastapi-framework/install-app:
      prime:
        - app/.env
        - app/app.py
        - app/webapp
        - app/templates
        - app/static

Some files, if they exist, are included by default. These include:
``app``, ``src``, ``<rock name>``, ``app.py``, ``migrate``, ``migrate.sh``,
``migrate.py``, ``static``, ``templates``.

**Regarding the migrate.sh file:**

If your app depends on a database it is common to run a database migration
script before app startup which, for example, creates or modifies tables.
This can be done by including the ``migrate.sh`` script in the root of your
project. It will be executed with the same environment variables and context
as the FastAPI application.

If the migration script fails, the app won't be started and the app charm
will go into blocked state. The migration script will be run on every unit
and it is assumed that it is idempotent (can be run multiple times) and that
it can be run on multiple units at the same time without causing issues. This
can be achieved by, for example, locking any tables during the migration.

Useful links
============

- :ref:`build-a-rock-for-a-fastapi-application`
