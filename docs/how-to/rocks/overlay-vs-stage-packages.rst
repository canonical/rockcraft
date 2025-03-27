.. _overlay-vs-stage-packages:

Overlay packages vs Stage packages
=====================================

Stage and Overlay are both steps within the :ref:`rocks lifecycle <lifecycle>`
and as such, they serve a similar purpose in terms of declaring which files
to copy to the next step (``stage`` vs ``overlay``), which packages to
install (``stage-packages`` vs ``overlay-packages``) and which instructions
to run, if any (``override-stage`` vs ``overlay-scripts``).

When to use each?
*********************

There are some differences when it comes to installing packages.
During the Overlay step, when a package is installed, the `maintainer scripts`_
are run as well. This behaviour puts a constraint in this step, since in order
to build the maintainer scripts, ``overlay-packages`` needs to run on the scope
of the ``base`` image, meaning that it cannot be used with bare bases
(``base: bare``) as there would not be anything supporting ``dpkg`` or ``apt``
for the maintainer scripts to run.

On the other hand, ``stage-packages`` do not run the maintainer scripts, which
makes it compatible with `chisel slices`_ and bare bases at the cost of manually
implementing the logic of maintainer scripts afterwards, if needed, e.g.
adding symlinks (not if using chisel slices) or adding a new internal user.

Using stage packages
--------------------

We will need to use stage packages every time we want to create a rock with a bare
base. In this case, we would declare a ``build-base``, install any build dependencies
in ``build-packages``, run the build step and then add to ``stage-packages`` any
package or slice we want to install in our ``base: bare``.

We can create a simple rock containing ``git``:

.. literalinclude:: ../code/overlay-vs-stage-packages/stage-example/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

Using overlay packages
----------------------

When using any ``base`` other than ``bare``, overlay packages can be used to
avoid installing the same packages in both build and stage, or when maintainer scripts
are required to run. The ``ca-certificates`` package is a good example of this, as
many other packages rely on symlinks created by the post installation script.

.. literalinclude:: ../code/overlay-vs-stage-packages/overlay-example/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

Example Using both approaches
*****************************

As explained at the beginning, both overlay and stage steps serve a similar purpose,
so there are common use cases that can be approached both ways.

In this example, we are going to create a simple ``curl`` rock using ``ubuntu@20.04``
as base. This version of ubuntu does not contain the ``ca-certificates`` package
which include the ssl certificates needed for ``curl`` to access secure sites using
HTTP over TLS (HTTPS).

.. tabs::

    .. group-tab:: Using overlay-packages

        The maintainer scripts of ``ca-certificates`` create a series of symbolic links
        under ``/etc/ssl/certs`` that are required for curl to access HTTPS sites. This
        is not a problem when using ``overlay-packages`` in our rockcraft.yaml file, as
        the maintainer scripts are run during the package installation in the overlay
        step:

        .. literalinclude:: ../code/overlay-vs-stage-packages/shared-example/overlay.yaml
            :caption: rockcraft.yaml
            :language: yaml

        Using the project file above, we can pack the rock:

        .. literalinclude:: ../code/overlay-vs-stage-packages/task.yaml
            :language: bash
            :start-after: [docs:pack-rock-shared-overlay]
            :end-before: [docs:pack-rock-shared-overlay-end]
            :dedent: 2

        Then skopeo copy it into docker daemon:

        .. literalinclude:: ../code/overlay-vs-stage-packages/task.yaml
            :language: bash
            :start-after: [docs:skopeo-shared-overlay]
            :end-before: [docs:skopeo-shared-overlay-end]
            :dedent: 2

        Once copied to docker daemon, we can fetch any HTTPS site using the new image. In
        this case, we are going to test that Canonical's website is reachable:

        .. code-block:: shell

            docker run ca-certs-example:0.1 exec curl https://canonical.com/

        The output should contain all the HTML code from Canonical's web page.

    .. group-tab:: Using stage-packages

        Since the maintainer scripts are required to run to have the symbolic links
        created when installing ``ca-certificates``, it would not be possible to use
        ``stage-packages``, making it impossible to create a curl rock with a bare
        base.

        However, there are `chisel slices`_ for both ``curl`` and ``ca-certificates``.
        Chisel slices already contain the symlinks needed and will copy them to the
        rock rootfs upon packing. This way, we can create a rockcraft project file
        to obtain a baseless image and achieve the same result, like so:

        .. literalinclude:: ../code/overlay-vs-stage-packages/shared-example/stage.yaml
            :caption: rockcraft.yaml
            :language: yaml

        Note that we have specified the chisel slices ``ca-certificates_data`` and
        ``curl_bins`` instead of ``ca-certificates`` and ``curl`` in ``stage-packages``.
        If we had specified those packages instead of the chisel slices, the required
        symbolic links would not be created due to the maintainer scripts not running.

        Once the rockcraft project file is created, we can pack the rock:

        .. literalinclude:: ../code/overlay-vs-stage-packages/task.yaml
            :language: bash
            :start-after: [docs:pack-rock-shared-stage]
            :end-before: [docs:pack-rock-shared-stage-end]
            :dedent: 2

        Then skopeo copy it into docker daemon:

        .. literalinclude:: ../code/overlay-vs-stage-packages/task.yaml
            :language: bash
            :start-after: [docs:skopeo-shared-stage]
            :end-before: [docs:skopeo-shared-stage-end]
            :dedent: 2

        Once copied to docker daemon, we can fetch any HTTPS site using the new image. In
        this case, we are going to test that Canonical's website is reachable:

        .. code-block:: shell

            docker run ca-certs-example:0.1 exec curl https://canonical.com/

        The output should contain all the HTML code from Canonical's web page.

.. _maintainer scripts: https://wiki.debian.org/MaintainerScripts
.. _chisel slices: https://documentation.ubuntu.com/rockcraft/en/latest/explanation/chisel
