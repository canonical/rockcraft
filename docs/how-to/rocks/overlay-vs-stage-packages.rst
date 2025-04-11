.. _overlay-vs-stage-packages:

Overlay packages vs Stage packages
=====================================

Stage and Overlay are both steps within the :ref:`parts lifecycle <lifecycle>`
and as such, they serve a similar purpose in terms of declaring which files
to copy to the next step, which packages to install or which instructions
to run during the current step, if any.

When to use each?
*********************

There are some differences when it comes to installing packages:

.. list-table::
   :widths: 50 30 30
   :header-rows: 1

   * -
     - ``stage-packages``
     - ``overlay-packages``
   * - Can be used with ``base: bare``
     - Yes
     - No\*
   * - Supports `chisel slices`_
     - Yes
     - No
   * - Execute the pkg's `maintainer scripts`_
     - No, unless Chisel slices are used
     - Yes
   * - Execution context
     - Sandboxed staging area in the build environment
     - The Ubuntu ``base``
   * - Modifies ``dpkg/status`` file
     - No
     - Yes

\* The reason ``overlay-packages`` cannot be used with bare bases is due to
the execution context. Since it runs on the Ubuntu ``base``, when ``bare`` is
specified there would not be anything supporting ``dpkg`` or ``apt``
for the maintainer scripts to run.

Side-by-side comparison
-----------------------

In this example, we are going to create a simple ``curl`` rock. This package
requires SSL certificates provided by the ``ca-certificates`` package in order
to access secure sites using HTTP over TLS (HTTPS).

.. tabs::

    .. group-tab:: Using overlay-packages


        .. literalinclude:: ../code/overlay-vs-stage-packages/overlay.yaml
            :caption: rockcraft.yaml
            :language: yaml

        The maintainer scripts of ``ca-certificates`` create a series of symbolic links
        under ``/etc/ssl/certs`` that are required for curl to access HTTPS sites. This
        is not a problem when using ``overlay-packages`` in our rockcraft.yaml file, as
        the maintainer scripts are run during the package installation in the overlay
        step. Then, using the project file above we can pack the rock and copy it to
        the docker daemon:

        .. literalinclude:: ../code/overlay-vs-stage-packages/task.yaml
            :language: bash
            :start-after: [docs:pack-rock-shared-overlay]
            :end-before: [docs:pack-rock-shared-overlay-end]
            :dedent: 2

        We can now fetch any HTTPS site using the new image. In this case, we are going
        to test that Canonical's website is reachable:

        .. code-block:: shell

            $ docker run ca-certs-example:0.1 exec curl https://canonical.com/

        The output should contain all the HTML code from Canonical's web page.

        Additionally, you can also use `dive`_ to see the fs of the resulting
        image:

        .. code-block:: shell

            $ dive ca-certs-example:0.1

        Note that since we are using ``overlay-packages`` we are constrained to
        use a Ubuntu base, which inevitably makes the resulting rock heavier than
        if we were using ``base: bare``.

    .. group-tab:: Using stage-packages


        .. literalinclude:: ../code/overlay-vs-stage-packages/stage.yaml
            :caption: rockcraft.yaml
            :language: yaml

        Since the maintainer scripts are required to run to have the symbolic links
        created when installing ``ca-certificates``, it would not be possible to use
        ``stage-packages``, making it impossible to create a curl rock with a bare
        base.

        However, there are `chisel slices`_ for both ``curl`` and ``ca-certificates``.
        Chisel slices already contain the symlinks needed and will copy them to the
        rock rootfs upon packing. This way, we can create a rockcraft project file
        to obtain a baseless image and achieve the same result, like the one above.

        Note that we have specified the chisel slices ``ca-certificates_data`` and
        ``curl_bins`` instead of ``ca-certificates`` and ``curl`` in ``stage-packages``.
        If we had specified those packages instead of the chisel slices, the required
        symbolic links would not be created due to the maintainer scripts not running.

        Once the rockcraft project file is created, we can pack the rock and copy it
        to the docker daemon:

        .. literalinclude:: ../code/overlay-vs-stage-packages/task.yaml
            :language: bash
            :start-after: [docs:pack-rock-shared-stage]
            :end-before: [docs:pack-rock-shared-stage-end]
            :dedent: 2

        Now we can fetch any HTTPS site using the new image. In
        this case, we are going to test that Canonical's website is reachable:

        .. code-block:: shell

            $ docker run ca-certs-example:0.1 exec curl https://canonical.com/

        The output should contain all the HTML code from Canonical's web page.

        Additionally, you can also use `dive`_ to see the fs of the resulting
        image:

        .. code-block:: shell

            $ dive ca-certs-example:0.1

        Note that since this approach uses a ``bare`` base, it is expected that
        the size of the resulting image is lower than if we were using any Ubuntu base.

.. _maintainer scripts: https://wiki.debian.org/MaintainerScripts
.. _chisel slices: https://documentation.ubuntu.com/rockcraft/en/latest/explanation/chisel
.. _dive: https://github.com/wagoodman/dive
