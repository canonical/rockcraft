.. _reference-rockcraft-yaml:

rockcraft.yaml
==============

This reference describes the purpose, usage, and examples of all available keys in a
rock's project file, ``rockcraft.yaml``.


.. _rockcraft-yaml-top-level-keys:

Top-level keys
--------------

.. kitbash-field:: craft_application.models.Project name

.. kitbash-field:: craft_application.models.Project title

.. kitbash-field:: rockcraft.models.Project summary

.. kitbash-field:: rockcraft.models.Project description

.. kitbash-field:: craft_application.models.Project version

.. kitbash-field:: rockcraft.models.Project base
    :override-type: Literal['ubuntu@20.04', 'ubuntu@22.04', 'ubuntu@24.04', 'ubuntu@25.10', 'ubuntu@26.04']

.. kitbash-field:: rockcraft.models.Project build_base
    :override-type: Literal['ubuntu@20.04', 'ubuntu@22.04', 'ubuntu@24.04', 'ubuntu@25.10', 'ubuntu@26.04', 'devel']

.. kitbash-field:: craft_application.models.Project source_code
    :override-type: str

.. kitbash-field:: craft_application.models.Project license

.. kitbash-field:: craft_application.models.Project contact
    :override-type: list[str]

.. kitbash-field:: craft_application.models.Project issues
    :override-type: list[str]

.. kitbash-field:: craft_application.models.Project adopt_info

.. kitbash-field:: rockcraft.models.Project environment

.. kitbash-field:: craft_application.models.Project package_repositories
    :override-type: list[repository]

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

.. kitbash-field:: craft_application.models.Project platforms

.. kitbash-field:: craft_application.models.Platform build_on
    :prepend-name: platforms.<platform-name>

.. kitbash-field:: craft_application.models.Platform build_for
    :prepend-name: platforms.<platform-name>


.. _rockcraft-yaml-part-keys:

Part keys
---------

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
