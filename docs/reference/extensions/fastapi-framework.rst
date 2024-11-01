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

1. ``fastapi`` needs to be declared as a requirement either in a
   ``requirements.txt`` file or within another ``pip`` supported
   requirement (eg. via ``pyproject.toml``).
2. The project must include a ASGI app in a variable called ``app`` in one of
   the following files relative to the project root (in order of priority):

   * ``app.py``
   * ``main.py``
   * ``__init__.py``, ``app.py`` or ``main.py`` within the ``app`` or ``src``
     directory or within a directory with the name of the rock as declared in
     ``rockcraft.yaml``.

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

Useful links
============

- :ref:`build-a-rock-for-a-fastapi-application`
