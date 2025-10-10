:tocdepth: 2

.. Check out the bottom of the page for the release template

Changelog
*********

.. _release-1.6.0:

1.6.0 (2024-Oct-17)
-------------------

Core
====

- Rockcraft 1.6.0 updates Pydantic, the internal library
  used to process ``rockcraft.yaml`` files, to a new major version. This change
  should not have any user-visible consequences, but please report any issues on
  `GitHub <https://github.com/canonical/rockcraft/issues>`_.
- Managed (non-destructive) runs now fail as expected if the build plan is
  empty. For example, trying to build a project with only ``amd64`` in its
  ``platforms`` will now fail when building on a non-amd64
  machine.
- ``package-repositories`` entries now support ``series`` and ``pocket`` for
  ``apt`` repositories, and ``key-id`` for PPAs.

Bases
#####

``bare``
""""""""

- ``bare``-based rocks now have a default ``PATH`` value set on the image,
  following the behaviour of ``Pebble`` services.

Plugins
#######

``poetry``
""""""""""

- Add a new plugin for Python projects that use the `Poetry`_ build system.

Extensions
##########

fastapi-framework
"""""""""""""""""

- Add a new ``fastapi-framework`` extension for `FastAPI`_-based projects.

flask-framework
"""""""""""""""

- On ``bare``-based rocks, the extension now uses Chisel slices for the Python
  interpreter.
- Add support for the ``ubuntu@24.04`` base.

django-framework
""""""""""""""""

- The ``django-framework`` extension is now stable and no longer requires the
  ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS`` environment variable.
- Add support for the ``ubuntu@24.04`` base.

go-framework
""""""""""""

- Add a new ``go-framework`` extension for Go-based projects.

Command line
============

- Improve reporting of builds that fail because they match multiple platforms.
- Improve error messages for invalid ``rockcraft.yaml`` files.
- The ``pack`` command now supports ``--shell`` and ``--shell-after``, and
  correctly handles cases where the packing itself fails and the ``--debug``
  argument is passed.
- The ``clean`` command now supports the ``--platform`` argument to filter which
  build environments to clean.
- Positional arguments are now correctly displayed on the ``help`` output of
  commands.
- The terminal cursor is now hidden during execution.

Init
====

- Add new ``--profile`` argument options for ``go-framework`` and
  ``fastapi-framework``.

Documentation
=============

- Add :ref:`reference documentation <craft_parts_poetry_plugin>` for the new
  ``poetry`` plugin.
- Add a :ref:`how-to guide <how-to-add-an-internal-user>`.
- Improve the ``flask-framework``
  :ref:`tutorial <build-a-rock-for-a-flask-application>` based on user feedback.
- Add a :ref:`tutorial <build-a-rock-for-a-django-application>` for the
  ``django-framework`` extension.
- Add a :ref:`tutorial <build-a-rock-for-a-fastapi-application>` for the
  ``fastapi-framework`` extension.

For a complete list of commits, check out the `1.6.0`_ release on GitHub.


.. _FastAPI:        https://fastapi.tiangolo.com
.. _Poetry:         https://python-poetry.org

.. _1.6.0:          https://github.com/canonical/rockcraft/releases/tag/1.6.0

..
  release template:

  X.Y.Z (YYYY-MMM-DD)
  -------------------

  Core
  ====

  # for everything related to the lifecycle of packing a rock

  Bases
  #####

  <ubuntu@xx.xx>
  """"""""""""""
  (order from newest base to oldest base)

  Plugins
  #######

  <plugin>
  """"""""

  Extensions
  ##########

  <extension>
  """""""""""

  Metadata
  ########

  Sources
  #######


  Command line
  ============

  # for command line and UX changes

  Init
  ====


  Documentation
  =============

  For a complete list of commits, check out the `X.Y.Z`_ release on GitHub.
