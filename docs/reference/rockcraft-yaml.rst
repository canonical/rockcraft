.. _reference-rockcraft-yaml:

rockcraft.yaml
==============

This reference describes the purpose, usage, and examples of all available keys in a
rock's project file, ``rockcraft.yaml``.


.. _rockcraft-yaml-top-level-keys:

Top-level keys
--------------

.. kitbash-field:: rockcraft.models.Project name

.. kitbash-field:: rockcraft.models.Project title

.. kitbash-field:: rockcraft.models.Project summary

.. kitbash-field:: rockcraft.models.Project description

.. kitbash-field:: rockcraft.models.Project version

.. kitbash-field:: rockcraft.models.Project base

.. kitbash-field:: rockcraft.models.Project build_base

.. kitbash-field:: rockcraft.models.Project source_code
    :override-type: str

.. kitbash-field:: rockcraft.models.Project license

.. kitbash-field:: rockcraft.models.Project contact
    :override-type: str | list[str]

.. kitbash-field:: rockcraft.models.Project issues
    :override-type: str | list[str]

.. kitbash-field:: rockcraft.models.Project package_repositories
  :override-type: list[dict[str, Any]]

.. kitbash-field:: rockcraft.models.Project adopt_info

.. kitbash-field:: rockcraft.models.Project environment

.. kitbash-field:: rockcraft.models.Project run_user

.. kitbash-field:: rockcraft.models.Project services

.. kitbash-field:: rockcraft.models.Project entrypoint_service

.. kitbash-field:: rockcraft.models.Project entrypoint_command

.. kitbash-field:: rockcraft.models.Project checks
    :override-type: dict[str, str]


.. _rockcraft-yaml-extensions:

extensions
~~~~~~~~~~

**Type**

``list[str]``

**Description**

The :ref:`extensions <reference-extensions>` to use in this project. During packing, the
boilerplate keys from the listed extensions will be added to the project file.

**Examples**

.. code-block:: yaml

    extensions:
      - expressjs-framework


.. _rockcraft-yaml-platform-keys:

Platform keys
-------------

.. kitbash-field:: rockcraft.models.Project platforms
    :override-type: dict[str, Platform]

.. kitbash-field:: craft_application.models.Platform build_on
    :prepend-name: platforms.<platform-name>
    :override-type: str | list[str]

.. kitbash-field:: craft_application.models.Platform build_for
    :prepend-name: platforms.<platform-name>
    :override-type: str | list[str]


.. _rockcraft-yaml-part-keys:

Part keys
---------

.. kitbash-field:: rockcraft.models.Project parts
    :override-type: dict[str, Part]

.. Main keys

.. kitbash-field:: craft_parts.parts.PartSpec plugin
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec after
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec disable_parallel
    :prepend-name: parts.<part-name>

.. Source keys

.. kitbash-field:: craft_parts.parts.PartSpec source
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec source_type
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec source_checksum
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec source_branch
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec source_tag
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec source_commit
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec source_depth
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec source_submodules
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec source_subdir
    :prepend-name: parts.<part-name>

.. Pull step keys

.. kitbash-field:: craft_parts.parts.PartSpec override_pull
    :prepend-name: parts.<part-name>

.. Overlay step keys

.. kitbash-field:: craft_parts.parts.PartSpec overlay_files
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec overlay_packages
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec overlay_script
    :prepend-name: parts.<part-name>

.. Build step keys

.. kitbash-field:: craft_parts.parts.PartSpec build_environment
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec build_attributes
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec override_build
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec build_packages
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec build_snaps
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec organize_files
    :prepend-name: parts.<part-name>

.. Stage step keys

.. kitbash-field:: craft_parts.parts.PartSpec stage_files
    :prepend-name: parts.<part-name>
    :override-type: list[str]

.. kitbash-field:: craft_parts.parts.PartSpec stage_packages
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec stage_snaps
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.parts.PartSpec override_stage
    :prepend-name: parts.<part-name>

.. Prime step keys

.. kitbash-field:: craft_parts.parts.PartSpec prime_files
    :prepend-name: parts.<part-name>
    :override-type: list[str]

.. kitbash-field:: craft_parts.parts.PartSpec override_prime
    :prepend-name: parts.<part-name>

.. Permission keys

.. kitbash-field:: craft_parts.parts.PartSpec permissions
    :prepend-name: parts.<part-name>

.. kitbash-field:: craft_parts.permissions.Permissions path
    :prepend-name: parts.<part-name>.permissions.<permission>

.. kitbash-field:: craft_parts.permissions.Permissions owner
    :prepend-name: parts.<part-name>.permissions.<permission>

.. kitbash-field:: craft_parts.permissions.Permissions group
    :prepend-name: parts.<part-name>.permissions.<permission>

.. kitbash-field:: craft_parts.permissions.Permissions mode
    :prepend-name: parts.<part-name>.permissions.<permission>
