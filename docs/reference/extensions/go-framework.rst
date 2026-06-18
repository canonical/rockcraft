.. meta::
    :description: Reference documentation for the Go framework extension, which configures Go in a rock and compiles and installs the Go binary.

.. _reference-go-framework:

Go framework
============

The Go extension streamlines the process of building Go application
rocks.

The extension builds and copies the Go binary file to the rock.
By default, the system foundation, or base, is set as ``bare`` to generate a
lightweight image.

.. note::
    The Go extension is compatible with the ``bare`` and ``ubuntu@24.04``
    bases.

.. _reference-go-framework-project-requirements:

Project requirements
--------------------

To use the ``go-framework`` extension, there must be a ``go.mod`` file
in the root directory of the project.

.. _reference-go-framework-organize:

App binary
----------

If the main package is in the base directory and the Rockcraft ``name``
attribute is equal to the Go module name, the name of the binary will
be selected correctly.

The ``organize`` key specifies a different binary to be used as the
main application, without having to override the service command. For example,
if a Go application contains a ``main`` package in the directory
``cmd/anotherserver``, the following snippet will override the main application
to use the binary ``anotherserver``:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    go-framework/install-app:
     organize:
       bin/anotherserver: usr/local/bin/<rockcraft project name>

.. _reference-go-framework-stage:

Included or excluded files
--------------------------

Some files, if they exist in the project root, are included by
default in the rock in the ``/app`` directory.  These include:
``migrate``, ``migrate.sh``, ``templates/`` and ``static/``.

The ``stage`` key of the ``go-framework/assets`` part
specifies the files to be included or excluded from
the rock upon ``rockcraft pack``, following the ``app/<filename>`` notation. For
example:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    go-framework/assets:
      stage:
        - app/migrate
        - app/migrate.sh
        - app/static
        - app/another_file_or_directory

The ``stage`` key supports glob patterns to define the list of files. See :ref:`filesets_explanation`
for the various ways you can specify files in your rock.

Adding the ``stage`` key to the project file overrides the default files to be included.
Files are excluded from the rock by defining ``stage`` and omitting the file to
be excluded.

Useful links
------------

:ref:`tutorial-build-a-rock-for-a-go-app`
