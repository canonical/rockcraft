.. _create_a_rootless_rock:

Creating a rootless rock
************************

A rootless roc does not require root privileges to be run, this means that ``root``
does not exist in this context and a new user is be created without such privileges.
There are two approaches when it comes to adding a new internal user to a rock,
depending on the situation you may want to:

- Use run-user:
    The :ref:`run-user <rockcraft_yaml_run_user>` field can be used
    in a rock's project file to specify the user that will run its services with.
    However, the ``run-user`` key only accepts a limited number of users, which could
    be a constraint for certain container applications, in which case we would need to
    take the second approach.

- Manually add a new user and group:
    In cases where the service running
    inside the rock is required to run with a specific user (e.g rabbitmq,
    apache, nginx, etc.) the build step must be overriden in the
    rock's project file to invoke ``useradd`` and ``groupadd`` commands.

Mandatory packages or slices
----------------------------

In any case, to add a new internal user or group to a rock, two packages or
their respective slices are needed:

- ``base-files``: to create the base folders such as ``/root`` and ``/home``,
- ``base-passwd``: to produce ``/etc/passwd`` and ``/etc/group`` files.

Creating the user and/or group
------------------------------

.. tabs::

    .. group-tab:: Using run-user

        ``run-user`` is declared at the root level of the rockcraft project file. It
        must be assigned a string which is the name of the new user that will be
        created and used to run the services inside the rock.

    .. group-tab:: Manually adding user and group

        Invoking the ``useradd`` and ``groupadd`` commands can take place in a part's
        :ref:`build <lifecycle>` step. This can be done by writing those commands in
        ``override-build`` key. However, the changes made by those commands will be
        only applied on the build instance, and will not be available in the resulting
        rock. Hence, ``$CRAFT_PART_INSTALL`` should be passed as the root directory to
        those two commands.

A full example
--------------

.. tabs::

    .. group-tab:: Using run-user

        The following project file illustrates how to use the ``useradd`` command
        in the ``override-build`` key inside a part.

        For an example of how to access the user inside the rock, here's a simple
        Python web service. The script will return an HTTP response containing the
        user that is running the web service:

        .. literalinclude:: ../code/rootless-rock/serve_user.py
            :language: python

        In the rockcraft project file, add the run-user field:

        .. literalinclude:: ../code/rootless-rock/using-run-user/rockcraft.yaml
            :caption: rockcraft.yaml
            :language: yaml
            :start-after: [docs:rock-run-user]
            :end-before: [docs:rock-run-user-end]

        Then, add the service, rockcraft will automatically run it with the
        ``_daemon_`` user:

        .. literalinclude:: ../code/rootless-rock/using-run-user/rockcraft.yaml
            :caption: rockcraft.yaml
            :language: yaml
            :start-after: [docs:rock-services]
            :end-before: [docs:rock-services-end]

        The final project file will look like this:

        .. literalinclude:: ../code/rootless-rock/using-run-user/rockcraft-clean.yaml
            :caption: rockcraft.yaml
            :language: yaml

        With the part and web service in place, build the rock:

        .. literalinclude:: ../code/rootless-rock/task.yaml
            :language: bash
            :start-after: [docs:pack-rock]
            :end-before: [docs:pack-rock-end]
            :dedent: 2

        Next, we will convert the rock from an OCI archive to a Docker image using
        Skopeo:

        .. literalinclude:: ../code/rootless-rock/task.yaml
            :language: bash
            :start-after: [docs:skopeo]
            :end-before: [docs:skopeo-end]
            :dedent: 2

        We can now check which internal user is running the service by running the
        image container:

        .. literalinclude:: ../code/rootless-rock/task.yaml
            :language: bash
            :start-after: [docs:check-user-run-user]
            :end-before: [docs:check-user-run-user-end]
            :dedent: 2

        The response should contain the new user name:

        .. code-block::

            Serving by _daemon_ on port 8080

    .. group-tab:: Manually adding user and group

        The following project file illustrates how to use the ``useradd`` command
        in the ``override-build`` key inside a part.

        For an example of how to access the user inside the rock, here's a simple
        Python web service. The script will return an HTTP response containing the
        user that is running the web service:

        .. literalinclude:: ../code/rootless-rock/serve_user.py
            :language: python

        Then, add a service to that runs the web service:

        .. literalinclude:: ../code/rootless-rock/manual-user-add/rockcraft.yaml
            :caption: rockcraft.yaml
            :language: yaml
            :start-after: [docs:rock-services]
            :end-before: [docs:rock-services-end]

        In the ``override-build`` section of the part, let's create a new user and a
        new group. We will also copy the Python script to a ``cgi-bin`` folder, and
        give it the execute permission:

        .. literalinclude:: ../code/rootless-rock/manual-user-add/rockcraft.yaml
            :caption: rockcraft.yaml
            :language: yaml
            :start-after: [docs:rock-build]
            :end-before: [docs:rock-build-end]

        The final project file will look like this:

        .. literalinclude:: ../code/rootless-rock/manual-user-add/rockcraft-clean.yaml
            :caption: rockcraft.yaml
            :language: yaml

        With the part and web service in place, build the rock:

        .. literalinclude:: ../code/rootless-rock/task.yaml
            :language: bash
            :start-after: [docs:pack-rock]
            :end-before: [docs:pack-rock-end]
            :dedent: 2

        Next, we will convert the rock from an OCI archive to a Docker image using
        Skopeo:

        .. literalinclude:: ../code/rootless-rock/task.yaml
            :language: bash
            :start-after: [docs:skopeo]
            :end-before: [docs:skopeo-end]
            :dedent: 2

        We can now check which internal user is running the service by running the
        image container:

        .. literalinclude:: ../code/rootless-rock/task.yaml
            :language: bash
            :start-after: [docs:check-user]
            :end-before: [docs:check-user-end]
            :dedent: 2

        The response should contain the new user name:

        .. code-block::

            Serving by myuser on port 8080
