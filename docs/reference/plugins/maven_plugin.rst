.. _rockcraft_maven_plugin:

Maven plugin
============

The Maven plugin builds Java projects using the Maven build tool.

After a successful build, this plugin will:

* Create ``jar/`` directory in ``$CRAFT_PART_INSTALL``.
* Hard link the ``.jar`` files generated in ``$CRAFT_PART_BUILD`` to
  ``$CRAFT_PART_INSTALL/jar``.
* Find the ``java`` executable provided by the part and link it as
  ``$CRAFT_PART_INSTALL/usr/bin/java`` if ``/usr/bin`` exists.


Keywords
--------

In addition to the common :ref:`plugin <reference-part-properties-plugin>` and
:ref:`sources <reference-part-properties-source>` keywords, this plugin
provides the following plugin-specific keywords:

maven-parameters
~~~~~~~~~~~~~~~~
**Type:** list of strings

Used to add additional parameters to the ``mvn package`` command line.


Environment variables
---------------------

This plugin reads the ``http_proxy`` and ``https_proxy`` variables
from the environment to configure Maven proxy access. A
comma-separated list of hosts that should not be accessed via proxy is
read from the ``no_proxy`` environment variable. The plugin writes the
proxy configuration in ``$CRAFT_PART_BUILD/.parts/.m2/settings.xml``.

This plugin will set the ``JAVA_HOME`` environment variable to the
path to the latest JDK found in the build environment.

Please refer to
`Configuring Apache Maven <https://maven.apache.org/configure.html>`_
for a list of environment variables used to configure Maven.

.. _rockcraft_maven-details-begin:

.. include:: /common/craft-parts/reference/plugins/maven_plugin.rst
   :start-after: .. _maven-details-begin:
   :end-before: .. _maven-details-end:

.. _rockcraft_maven-details-end:

.. include:: /common/craft-parts/reference/plugins/maven_plugin.rst
   :start-after: .. _maven-details-end:
