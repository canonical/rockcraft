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
By default, the system foundation, or base, is set as ``bare`` to generate a
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
2. The project must include an
   `Asynchronous Server Gateway Interface (ASGI) <https://asgi.readthedocs.io/en/latest/>`__ app
   in a variable called ``app`` in one of the following files relative to the project
   root (in order of precedence):

   * ``app.py``
   * ``main.py``
   * ``__init__.py``, ``app.py`` or ``main.py`` within the ``app`` or ``src``
     directory or within a directory with the name of the rock as declared in
     the project file.

.. _reference-fastapi-framework-uv:

uv projects
-----------

If both a ``uv.lock`` and a ``pyproject.toml`` file are present in the project
root, the extension builds the application with the :doc:`uv plugin
</reference/plugins/uv_plugin>` instead of the Python plugin, installing dependencies
from the lockfile with ``uv sync``. Uvicorn is injected after the build step
regardless of the lockfile contents. In this case a ``requirements.txt`` file is
not required.

If only ``pyproject.toml`` is present (no ``uv.lock``), the extension falls back
to the Python plugin. If ``uv.lock`` is present but ``pyproject.toml`` is
missing, packing fails with an error, as the uv plugin requires both files.

.. _reference-fastapi-framework-stage-packages:

App dependencies
----------------

The ``stage-packages`` key specifies all additional dependencies. If the FastAPI app
has its own special dependencies, this key must declare them.

The following example specifies the ``libpq-dev`` package:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    fastapi-framework/dependencies:
      stage-packages:
        # list required packages or slices for your FastAPI application below.
        - libpq-dev

.. _reference-fastapi-framework-prime:

Included or excluded files
--------------------------

Some files, if they exist, are included by default in the rock. These include:
``app``, ``src``, ``<rock name>``, ``app.py``, ``migrate``, ``migrate.sh``,
``migrate.py``, ``static``, ``templates``.

The ``prime`` key specifies the files to be included or excluded from
the rock upon ``rockcraft pack``, following the ``app/<filename>`` notation. For
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

The ``prime`` key supports glob patterns to define the list of files. See :ref:`filesets_explanation`
for the various ways you can specify files in your rock.

Adding the ``prime`` key to the project file overrides the default files to be included.
Files are excluded from the rock by defining ``prime`` and omitting the file to
be excluded.

Useful links
------------

:ref:`tutorial-build-a-rock-for-a-fastapi-app`
