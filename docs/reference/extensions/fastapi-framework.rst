.. meta::
    :description: Reference documentation for the FastAPI framework extension, which configures FastAPI in a rock and populates it with FastAPI dependencies such as Uvicorn.

.. _reference-fastapi-framework:

FastAPI framework
=================

The FastAPI extension streamlines the process of building FastAPI application
rocks.

It facilitates the installation of FastAPI application dependencies, including
Uvicorn, inside the rock. Additionally, it transfers your project files to
``/app`` within the rock.
By default, the :ref:`base <explanation-bases>` ``bare`` is used to generate a
lightweight image.

.. note::
    The FastAPI extension is compatible with the ``bare`` and ``ubuntu@24.04``
    bases.

.. _reference-fastapi-framework-project-requirements:

Project requirements
--------------------

There are 2 requirements to be able to use the ``fastapi-framework`` extension:

1. There must be a ``requirements.txt`` file in the root of the project with
   ``fastapi`` declared as a dependency
2. The project must include an `ASGI <https://asgi.readthedocs.io/en/latest/>`__ app
   in a variable called ``app`` in one of the following files relative to the project
   root (in order of priority):

   * ``app.py``
   * ``main.py``
   * ``__init__.py``, ``app.py`` or ``main.py`` within the ``app`` or ``src``
     directory or within a directory with the name of the rock as declared in
     the project file.

.. _reference-fastapi-framework-stage-packages:

Specifying required dependencies
--------------------------------

Use the ``stage-packages`` key to specify any dependencies required for your FastAPI
application. In the following example we use it to specify ``libpq-dev``:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    fastapi-framework/dependencies:
      stage-packages:
        # list required packages or slices for your FastAPI application below.
        - libpq-dev

Adding this key is optional unless your application requires additional dependencies.

.. _reference-fastapi-framework-prime:

Including or excluding files in your rock
-----------------------------------------

Some files, if they exist, are included by default in your rock. These include:
``app``, ``src``, ``<rock name>``, ``app.py``, ``migrate``, ``migrate.sh``,
``migrate.py``, ``static``, ``templates``.

Use the ``prime`` field to specify the files to be included or excluded from
your rock upon ``rockcraft pack``. Follow the ``app/<filename>`` notation. For
example:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    fastapi-framework/install-app:
      prime:
        - app/.env
        - app/app.py
        - app/webapp
        - app/templates
        - app/static

You can use glob patterns to define your list of files; see :ref:`filesets_explanation`
for more details.

Adding the ``prime`` key to your project file overrides the default files to be included.
Exclude a file from your rock by defining ``prime`` and omitting the file that you
want to exclude.

Useful links
------------

:ref:`tutorial-build-a-rock-for-a-fastapi-app`
