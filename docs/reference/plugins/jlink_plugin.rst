.. _rockcraft_jlink_plugin:

JLink plugin
=============

The JLink plugin can be used for Java projects where you would want to
deploy Java runtime specific for your application or install a minimal
Java runtime.


Keywords
--------

This plugin uses the common :ref:`plugin <part-properties-plugin>` keywords as
well as those for :ref:`sources <part-properties-sources>`.

Additionally, this plugin provides the plugin-specific keywords defined in the
following sections.

jlink-java-version
~~~~~~~~~~~~~~~~~~~
**Type:** str

Java package version to use for the build (e.g. 21 will install openjdk-21-jdk).

jlink-jars
~~~~~~~~~~~~~~~~~~
**Type:** list of strings

List of paths to jar files of your application. If not specified, plugin
will find all jar files in the staging area.

Dependencies
------------

By default this plugin uses openjdk-21-jdk from the build base.

The user is expected to stage openjdk dependencies either by installing
an appropriate openjdk slice:

.. code-block:: yaml

    parts:
        runtime:
            plugin: jlink
            after:
                - deps

        deps:
            plugin: nil
            stage-packages:
                - openjdk-21-jre-headless_security

or by installing the dependencies directly:

.. code-block:: yaml

    parts:
        runtime:
            plugin: jlink
            after:
                - deps

        deps:
            plugin: nil
            stage-packages:
                - libc6_libs
                - libgcc-s1_libs
                - libstdc++6_libs
                - zlib1g_libs
                - libnss3_libs


How it works
------------

During the build step, the plugin performs the following actions:

* Finds all jar files in the staging area or selects jars specified in
  _jlink_jars_.
* Unpacks jar files to the temporary location and concatenates all embedded jars
  into `jdeps <https://docs.oracle.com/en/java/javase/21/docs/specs/man/jdeps.html>`_
  classpath.
* Runs `jdeps <jdeps_>`_ to discover Java modules required for the staged jars.
* Runs `jlink <https://docs.oracle.com/en/java/javase/21/docs/specs/man/jlink.html>`_
  to create a runtime image from the build JDK.
