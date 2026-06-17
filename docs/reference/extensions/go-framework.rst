.. _reference-go-framework:

Go framework
============

The Go extension streamlines the process of building Go application
rocks.

The extension builds and copies the Go binary file to the rock.
By default, the :ref:`base <explanation-bases>` ``bare`` is used to generate
a lightweight image.

.. note::
    The Go extension is compatible with the ``bare`` and ``ubuntu@24.04``
    bases.

.. _reference-go-framework-project-requirements:

Project requirements
--------------------

To use the ``go-framework`` extension, there must be a ``go.mod`` file
in the root directory of the project.

.. _reference-go-framework-organize:

Specifying a different binary for your app
------------------------------------------

If the main package is in the base directory and the rockcraft name
attribute is equal to the go module name, the name of the binary will
be selected correctly, otherwise you will need to adjust it.

Use the ``organize`` key to specify a different binary to be used as the
main application, without having to override the service command. For example,
if your Go application contains a ``main`` package in the directory
``cmd/anotherserver``, the name of the binary will be ``anotherserver``
and you can override the main application to use the binary with the
next snippet:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    go-framework/install-app:
     organize:
       bin/anotherserver: usr/local/bin/<rockcraft project name>

.. _reference-go-framework-stage:

Including or excluding files in your rock
-----------------------------------------

Some files, if they exist in the project root, are included by
default in the rock in the ``/app`` directory.  These include:
``migrate``, ``migrate.sh``, ``templates/`` and ``static/``.

You can customise the files to include by overriding the ``stage`` property
of the ``go-framework/assets`` part:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    go-framework/assets:
      stage:
        - app/migrate
        - app/migrate.sh
        - app/static
        - app/another_file_or_directory


You can use glob patterns to define your list of files. See :ref:`filesets_explanation`
for the various ways you can specify files in your rock.

Adding the ``stage`` field to your project file overrides the default files to be included.
Exclude a file from your rock by defining ``stage`` and omitting the file that you
want to exclude.

Useful links
------------

:ref:`tutorial-build-a-rock-for-a-go-app`
