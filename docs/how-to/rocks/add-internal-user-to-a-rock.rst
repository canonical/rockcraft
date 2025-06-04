.. _add_internal_user_to_a_rock:

How to add a new internal user to a rock
*****************************************

You can declare :ref:`run-user <rockcraft_yaml_run_user>` in a rock's project
file to specify which user you want to run a its services with. If you don't
specify a user, the services run as root by default. The ``run-user`` key only
accepts a limited number of users, which could be a constraint for certain
container applications.

Mandatory packages or slices
----------------------------

To add a new internal user or group to a rock, two packages or their respective
slices are needed:

- ``base-files``: to create the base folders such as ``/root`` and ``/home``,
- ``base-passwd``: to produce ``/etc/passwd`` and ``/etc/group`` files.

Creating the user and/or group
------------------------------

Invoking the ``useradd`` and ``groupadd`` commands can take place in a part's
:ref:`build <lifecycle>` step. This can be done by writing those commands in
``override-build`` key. However, the changes made by those commands will be
only applied on the build instance, and will not be available in the resulting
rock. Hence, ``$CRAFT_PART_INSTALL`` should be passed as the root directory to
those two commands.

A full example
--------------

The following project file illustrates how to use the ``useradd`` command
in the ``override-build`` key inside a part.

For an example of how to access the user inside the rock, here's a simple
Python web service. The script will return an HTTP response containing the
user that is running the web service:

.. literalinclude:: ../code/internal-user/serve_user.py
    :language: python

Then, add a service to that runs the web service:

.. literalinclude:: ../code/internal-user/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml
    :start-after: [docs:rock-services]
    :end-before: [docs:rock-services-end]

In the ``override-build`` section of the part, let's create a new user and a
new group. We will also copy the Python script to a ``cgi-bin`` folder, and
give it the execute permission:

.. literalinclude:: ../code/internal-user/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml
    :start-after: [docs:rock-build]
    :end-before: [docs:rock-build-end]

The final project file will look like this:

.. literalinclude:: ../code/internal-user/rockcraft-clean.yaml
    :caption: rockcraft.yaml
    :language: yaml

With the part and web service in place, build the rock:

.. literalinclude:: ../code/internal-user/task.yaml
    :language: bash
    :start-after: [docs:pack-rock]
    :end-before: [docs:pack-rock-end]
    :dedent: 2

.. tabs::

    .. group-tab:: Docker

        Next, we will convert the rock from an OCI archive to a Docker image using
        Skopeo:

        .. literalinclude:: ../code/internal-user/task.yaml
            :language: bash
            :start-after: [docs:skopeo]
            :end-before: [docs:skopeo-end]
            :dedent: 2

        We can now check which internal user is running the service by running the
        image container:

        .. literalinclude:: ../code/internal-user/task.yaml
            :language: bash
            :start-after: [docs:check-user]
            :end-before: [docs:check-user-end]
            :dedent: 2

        The response should contain the new user name:

    .. group-tab:: Podman

        Next, we can run the rock directly using Podman:

        .. literalinclude:: ../code/internal-user/task.yaml
            :language: bash
            :start-after: [docs:check-user-podman]
            :end-before: [docs:check-user-podman-end]
            :dedent: 2

.. code-block::

    Serving by myuser on port 8080
