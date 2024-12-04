.. _rockcraft_ant_plugin:

Ant plugin
==========

The Ant plugin builds Java projects using the
`Apache Ant <https://ant.apache.org/>`_ build tool.

After a successful build, this plugin will:

* Create ``jar/`` directory in ``$CRAFT_PART_INSTALL``.
* Hard link the ``.jar`` files generated in ``$CRAFT_PART_BUILD`` to
  ``$CRAFT_PART_INSTALL/jar``.
* Find the ``java`` executable provided by the part and link it as
  ``$CRAFT_PART_INSTALL/usr/bin/java`` if ``/usr/bin`` exists.


Keywords
--------

In addition to the common :ref:`plugin <part-properties-plugin>` and
:ref:`sources <part-properties-sources>` keywords, this plugin provides
the following plugin-specific keywords:

ant-build-targets
~~~~~~~~~~~~~~~~~
**Type:** list of strings

The ant targets to build. These are directly passed to the ``ant`` command line.

ant-build-file
~~~~~~~~~~~~~~
**Type:** str

The name of the main XML build file. Defaults to ``build.xml``.

ant-properties
~~~~~~~~~~~~~~
**Type:** dict of strings to strings

A series of key: value pairs that are passed to ``ant`` as properties using the
``-D{key}={value}`` notation.


Environment variables
---------------------

This plugin reads the ``http_proxy`` and ``https_proxy`` variables from
the environment to configure proxy access.

Please refer to
`Running Apache Ant <https://ant.apache.org/manual/running.html>`_ for
a list of environment variables used by Ant.

.. _rockcraft_ant-details-begin:

.. include:: /common/craft-parts/reference/plugins/ant_plugin.rst
   :start-after: .. _ant-details-begin:
   :end-before: .. _ant-details-end:

.. _rockcraft_ant-details-end:

.. include:: /common/craft-parts/reference/plugins/ant_plugin.rst
   :start-after: .. _ant-details-end:
