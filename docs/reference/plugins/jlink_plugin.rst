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

jlink-slice-deps
~~~~~~~~~~~~~~~~~~
**Type:** list of strings

List of dependent slices required for the Java runtime. By default jlink
plugin deploys openjdk-21-jre-headless_core slice.

Dependencies
------------

By default this plugin uses openjdk-21-jdk from the build base.


How it works
------------

During the build step, the plugin performs the following actions:

* Installs dependent slices (openjdk-21-jre-headless_core and base_files_base)
  by default to the staging area.
* Finds all jar files in the staging area
* Unpacks jar files to the temporary location and concatenates all embedded jars
  into classpath.
* Runs jdeps to discover Java modules required for the staged jars.
* Runs jlink to create a runtime image using build.
