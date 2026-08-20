.. meta::
    :description: Reference documentation for the Express framework extension, which configures Express in a rock and installs Node.js and the app's dependencies.

.. _reference-express-framework:

Express framework
=================

The Express extension streamlines the process of building Express
application rocks. It facilitates the installation of Express application dependencies, including
Node.js and npm, inside the rock.

.. tab-set::
    .. tab-item:: Ubuntu 22.04 and 24.04
        :sync: base-22-24

        Additionally, it transfers your project files
        to ``/app`` within the rock.

    .. tab-item:: Ubuntu 26.04 and higher
        :sync: base-26-plus

        The extension discovers the location of the
        ``package.json``, but the extension can only package a single application.

By default, the system foundation, or base, is set as ``bare`` to generate a
lightweight image.
The Express extension is compatible with the ``bare``, ``ubuntu@24.04`` and ``ubuntu@26.04``
bases.

.. _reference-express-framework-project-requirements:

Project requirements
--------------------

.. tab-set::
    .. tab-item:: Ubuntu 22.04 and 24.04
        :sync: base-22-24

        There are three requirements to be able to use the ``expressjs-framework``
        extension:

        - The application should reside in the ``app`` directory.
        - The application should have a ``package.json`` file.
        - The ``package.json`` file should define the ``start`` script.

        For more information, see the `npm documentation <https://docs.npmjs.com/cli/v11/configuring-npm/package-json>`_.

    .. tab-item:: Ubuntu 26.04 and higher
        :sync: base-26-plus

        There are two requirements to be able to use the ``expressjs-framework``
        extension:

        - The application should have a ``package.json`` file in the same
          directory as ``rockcraft.yaml`` file or one directory below the ``rockcraft.yaml`` file.
        - The ``package.json`` file should define the ``start`` script.

        For more information, see the `npm documentation <https://docs.npmjs.com/cli/v11/configuring-npm/package-json>`_.

        If the application defines a ``build`` script in its ``package.json`` file, it is
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
If you don't customize the version of node, it will be installed from the
`Ubuntu package repository <https://packages.ubuntu.com/noble/nodejs>`_.

.. _reference-express-framework-stage-packages:

Additional runtime packages
---------------------------

Installing additional runtime packages is currently unsupported.


Useful links
------------

:ref:`tutorial-build-a-rock-for-an-express-app`
