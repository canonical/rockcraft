.. _explanation-usrmerge-implementation:

Usrmerge implementation
=======================

Usrmerge is a collection of methods for combining the ``/usr`` directories in the Linux
filesystem hierarchy. Because there's no single cross-compatible solution recommended
by the `Filesystem Hierarchy Standard <https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html>`_,
different Linux distributions have provided different solutions to this problem over
time.

Rocks can contain Ubuntu as a baseline system, so Rockcraft must also contend with
usrmerge. This page explains how its usrmerge implementation works.

Merge conflicts
---------------

For a long period in Linux filesystem design, executables were placed either in the
``/bin`` or ``/usr/bin`` directories at the discretion of the developer. However, over
time, a consensus developed that the two directories should be combined, for simplicity
and a compatibility between different Linux distributions. Across many distributions,
this has most commonly resulted in ``/bin`` becoming a symbolic link to ``/usr/bin``.
For Ubuntu, the first long-term release with this behavior was Ubuntu 24.04 LTS.

Conflicts occur when different pieces of software inside a Linux system disagree about
what type of filesystem object ``/bin`` should be. Plugins in Rockcraft place their
final files into ``/bin``. They create ``/bin`` as a regular directory if it does not
exist either as a directory or a link, but other packages may expect ``/bin`` to be a
symbolic link to ``/usr/bin``, resulting in a file conflict.

As an example, consider the following rock project snippet:

.. code-block:: yaml

    parts:
      my-go-project:
        plugin: go
        source: .

      my-dependencies:
        plugin: nil
        stage-packages:
          - base-files

This rock succeeds when building with the ``ubuntu@22.04`` base, creating a single
``/bin/my-go-project`` executable when ``/bin`` is a directory. However, building the
same rock with ``ubuntu@24.04`` will fail, as this new version of ``base-files`` creates
``/bin`` as a symbolic link to ``/usr/bin``. Then, ``my-go-project`` stages
``/bin/my-go-project``. Since ``/bin`` can't be both a regular directory and a symbolic
link, a conflict arises.

Merging ``/usr`` directories in rocks
-------------------------------------

When designing a usrmerge solution for rocks, the priority was to fix the problem for
future rocks. The solution had to avoid any assumptions about the part's existing file
structure. In addition, while the merge should be automatic for those who don't wish to
worry about it, it had to also allow users to opt in or out of the behavior in order to
support older rocks.

To serve these goals, at the start of the pull step of the lifecycle, Rockcraft ensures
the install directory of a part is pre-populated with the appropriate directories and
symbolic links. This means that inside a part, ``bin`` is always linked to ``usr/bin``,
adhering to the newer standard and disambiguating the files before plugins have a chance
to create a regular ``bin`` directory. While this does not impact the final artifact, it
does impact what files are available during the build process.

Plugin syntax and compatibility
-------------------------------

The usrmerge implementation is automatically enabled when building with the
``ubuntu@25.10`` base and higher. It can be opted into for bases lower than
``ubuntu@25.10`` with the ``enable-usrmerge`` build attribute, or disabled on newer
bases with ``disable-usrmerge``.

All plugins are affected by these changes, except for the :ref:`craft_parts_dump_plugin`
and :ref:`craft_parts_nil_plugin`. These plugins serve a different niche than language
plugins, providing a means to customize the process. Due to this, they leave it up to
the project to properly organize and stage their outputs – it didn't make sense to
enforce a filesystem structure onto them.

With usrmerge, any :doc:`override-build scripts
</common/craft-parts/how-to/override_build>` are subject to breaking. Since these are
entirely free-form Bash scripts, it's plausible that some are written with the
assumption that ``/bin`` will be a plain directory. To resolve this potential conflict,
the following build attributes are available:

.. list-table::
    :header-rows: 1
    :widths: 10 30

    * - Key
      - Effect

    * - ``enable-usrmerge``
      - When building on ``ubuntu@24.04`` and lower, this build attribute can be used to
        forcefully enable creating the base files.

    * - ``disable-usrmerge``
      - When building on ``ubuntu@25.10`` and higher, this build attribute can be used
        to forcefully disable creating the base files.
