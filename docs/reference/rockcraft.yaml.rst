.. _rockcraft.yaml_reference:

rockcraft.yaml
==============

.. include:: rock_parts/toc.rst

A Rockcraft project is defined in a YAML file named ``rockcraft.yaml`` at the
root of the project tree in the filesystem. This file is commonly known as the
*project file*.

This reference describes the configuration keys available in this file.


Format specification
--------------------

.. note::
   The keys ``entrypoint``, ``cmd`` and ``env`` are not supported in
   Rockcraft. All rocks have Pebble as their entrypoint, and thus you must use
   ``services`` to define your container application.

.. py:currentmodule:: craft_application.models.project

.. kitbash-field:: Project name

    The value must conform with Pebble's format for layer files.

.. kitbash-field:: Project title

    The human-readable title of the rock. If omitted, defaults to ``name``.

.. py:currentmodule:: rockcraft.models.project

.. kitbash-field:: Project summary

.. kitbash-field:: Project description

.. py:currentmodule:: craft_application.models.project
.. kitbash-field:: Project version

.. https://github.com/canonical/pydantic-kitbash/issues/76
..    Used to tag the OCI image and name the rock file.

.. _rockcraft_yaml_base:
.. py:currentmodule:: rockcraft.models.project
.. kitbash-field:: Project base
    :override-type: ubuntu@20.04 | ubuntu@22.04 | ubuntu@24.04 | ubuntu@25.10 | bare

.. Type override due to https://github.com/canonical/pydantic-kitbash/issues/68

.. note::
   The notation "ubuntu:<channel>" is also supported for some channels, but this
   format is deprecated and should be avoided.

.. _rockcraft_yaml_build_base:

.. kitbash-field:: Project build_base
    :override-type: ubuntu@20.04 | ubuntu@22.04 | ubuntu@24.04 | ubuntu@25.10 | devel

.. Type override due to https://github.com/canonical/pydantic-kitbash/issues/68

.. note::
   The notation "ubuntu:<channel>" is also supported for some channels, but this
   format is deprecated and should be avoided.

.. note::
   ``devel`` is a "special" value that means "the next Ubuntu version, currently
   in development". This means that the contents of this system changes
   frequently and should not be relied on for production rocks.

.. py:currentmodule:: craft_application.models.project
.. kitbash-field:: Project license

    The special value ``proprietary`` can also be used.

.. The blockquote above is due to https://github.com/canonical/pydantic-kitbash/issues/77

.. _rockcraft_yaml_run_user:

.. py:currentmodule:: rockcraft.models.project
.. kitbash-field:: Project run_user

.. kitbash-field:: Project environment

.. note::
    String interpolation is not yet supported so any attempts to dynamically
    define environment variables with ``$`` will end in a project
    validation error.

.. kitbash-field:: Project services

.. kitbash-model:: Service
    :prepend-name: services.<service-name>
    :skip-description:

.. _rockcraft-yaml-entrypoint-service:

.. kitbash-field:: Project entrypoint_service

.. warning::
   This option must only be used in cases where the targeted deployment
   environment has unalterable assumptions about the container image's
   entrypoint.

.. _rockcraft-yaml-entrypoint-command:

.. kitbash-field:: Project entrypoint_command

.. caution::
    You should only set this key for certain categories of general-purpose rocks where
    Pebble services aren't appropriate, such as the Ubuntu OS and base images.

.. kitbash-field:: Project checks

    The ``http``, ``tcp`` and ``exec`` fields are mutually exclusive and determine the
    check type.

.. py:currentmodule:: rockcraft.pebble
.. kitbash-model:: _BaseCheck
    :prepend-name: checks.<check-name>
    :skip-description:

.. kitbash-model:: HttpCheckOptions
    :prepend-name: checks.<check-name>.http

.. kitbash-model:: TcpCheckOptions
    :prepend-name: checks.<check-name>.tcp

.. kitbash-model:: ExecCheckOptions
    :prepend-name: checks.<check-name>.exec

.. _platforms:

.. py:currentmodule:: craft_application.models.project
.. kitbash-field:: Project platforms

.. warning::
   **All** target architectures must be compatible with the architecture of
   the host where Rockcraft is being executed (i.e. emulation is not supported
   at the moment).

.. kitbash-model:: Platform
    :prepend-name: platforms.<platform-name>

.. note::
   At the moment Rockcraft will only build for a single architecture, so
   if provided ``build-for`` must be a single string or a list with exactly one
   element.

.. kitbash-field:: Project parts
    :override-type: dict[str, Part]

    General part properties can be found in the :ref:`reference-part-properties`
    reference. Specific plugin properties can be found in the relevant
    :doc:`plugin reference <plugins>`

``extensions``
~~~~~~~~~~~~~~

**Type**: list[string]

**Required**: No

Extensions to enable when building the ROCK.

Currently supported extensions:

- ``flask-framework``
- ``django-framework``
- ``go-framework``
- ``fastapi-framework``
- ``expressjs-framework``
- ``spring-boot-framework``

Example
-------

.. literalinclude:: code/example/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml


.. _`Pebble Layer Specification format`:  https://canonical-pebble.readthedocs-hosted.com/en/latest/reference/layer-specification/
