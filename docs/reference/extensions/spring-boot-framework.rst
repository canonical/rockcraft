.. meta::
    :description: Reference documentation for the Spring Boot framework extension, which configures Spring Boot in a rock and packages the JAR using Maven or Gradle.

.. _reference-spring-boot-framework:

Spring Boot framework
=====================

The Spring Boot extension streamlines the process of building Spring Boot
application rocks.

The extension packs and copies the Jar package file to the rock.
By default, the system foundation, or base, is set as ``bare`` to generate a
lightweight image.

.. note::

    The Spring Boot extension is compatible with the ``bare`` and
    ``ubuntu@24.04`` bases.

.. _reference-spring-boot-framework-project-requirements:

Project requirements
--------------------

To use the Spring Boot Framework extension, there must be either:

- a ``pom.xml`` file
- a ``build.gradle`` file

in the root directory of the project.
The project must not contain both files, otherwise the rock initialization will fail.

For the build process to execute correctly, the ``mvnw`` or
``gradlew`` wrapper must have executable permissions.

.. _reference-spring-boot-framework-plugin:

Maven or Gradle usage
---------------------

The ``spring-boot-framework`` extension dynamically determines the plugin to
use to build the rock. Depending on the presence of ``pom.xml`` or
``build.gradle`` file, the extension will use either the
:doc:`maven </common/craft-parts/reference/plugins/maven_plugin>` or
:doc:`gradle </common/craft-parts/reference/plugins/gradle_plugin>` plugin,
respectively.

.. code-block:: yaml
  :caption: rockcraft.yaml

  # if pom.xml is present, use maven plugin
  parts:
    spring-boot-framework/install-app:
      plugin: maven
      maven-use-wrapper: False # If mvnw file is present, True


.. code-block:: yaml
  :caption: rockcraft.yaml

  # if build.gradle is present, use gradle plugin
  parts:
    spring-boot-framework/install-app:
      plugin: gradle
      gradle-task: bootJar

.. _reference-spring-boot-framework-build-packages:

Java version
------------

By default, the ``spring-boot-framework`` uses ``default-jdk`` package to build
the rock. Depending on the ``build-base``, a different Java JDK version is used.
To find out what Java version is used to pack the JAR, you can search the
`Ubuntu package archive <https://packages.ubuntu.com/>`_.

The ``build-packages`` key specifies the Java version for the rock.
For example:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    spring-boot-framework/install-app:
      build-packages:
        - openjdk-17-jdk # specify the Java package to use

.. _reference-spring-boot-framework-runtime:

JLink plugin
------------

To provide an efficient runtime for Java, the extension calls the
:doc:`Jlink </common/craft-parts/reference/plugins/jlink_plugin>`
plugin to trim out any unused parts of the JDK. This reduces the size
of the rock and improves performance.

The ``spring-boot-framework`` uses the following configuration:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    spring-boot-framework/runtime:
      plugin: jlink
      source: .
      build-packages:
        - default-jdk
      stage-packages: # these packages are required for bare base rocks.
        - bash_bins
        - ca-certificates_data
        - coreutils_bins
        - base-files_tmp

.. _reference-spring-boot-framework-stage:

Included or excluded files
--------------------------

If ``migrate`` or ``migrate.sh`` exist in the project's root directory, they will be
included in the rock's ``/app`` directory by default.

The ``stage`` key of the ``spring-boot-framework/assets`` part
specifies the files to be included or excluded from
the rock upon ``rockcraft pack``, following the ``app/<filename>`` notation. For
example:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    spring-boot-framework/assets:
      stage:
        - app/migrate
        - app/migrate.sh
        - app/another_file_or_directory

The ``stage`` key supports glob patterns to define the list of files. See :ref:`filesets_explanation`
for the various ways you can specify files in your rock.

Adding the ``stage`` key to the project file overrides the default files to be included.
Files are excluded from the rock by defining ``stage`` and omitting the file to
be excluded.

Useful links
------------

:ref:`tutorial-build-a-rock-for-a-spring-boot-app`
