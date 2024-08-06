.. _add_internal_user_in_rocks:

How to add an internal user to a rock
*************************************

Rockcraft allows you to use :ref:`run-user <rockcraft_yaml_run_user>` to
specify the user you want to run the rock's service(s) with. Without using that
field in the ``rockcraft.yaml`` file, the service(s) will be run by the root
user. However, ``run-user`` only accepts a limited amount of well-known users,
which could become a constraint for certain container applications.

In order to add a new internal user or group to a rock, two packages (or their
respective slices) are needed:

- ``base-files``: to create the base dirs such as ``/root`` and ``/home``,
- ``base-passwd``: to produce basic ``/etc/passwd`` and ``/etc/group`` files.

Invoking the ``useradd`` and ``groupadd`` commands can take place in the
:ref:`build <lifecycle>` step. However, the changes made by those commands will
be only applied on the build instance, and will not be available in the
resulting rock. Hence, ``$CRAFT_PART_INSTALL`` should be passed as the root
directory to those two commands.

The following ``rockcraft.yaml`` illustrates how to use ``useradd`` command in
the ``override-build`` field inside a part.

.. literalinclude:: ../code/internal-user/rockcraft.yaml
    :language: yaml
    :start-after: [docs:rock-parts]
    :end-before: [docs:rock-parts-end]

Furthermore, let's add a service that tests the running user by executing
``whoami``:

.. literalinclude:: ../code/internal-user/rockcraft.yaml
    :language: yaml
    :start-after: [docs:rock-services]
    :end-before: [docs:rock-services-end]

Moving along, the rock can be built by running:

.. literalinclude:: ../code/internal-user/task.yaml
    :language: bash
    :start-after: [docs:pack-rock]
    :end-before: [docs:pack-rock-end]
    :dedent: 2

We can test the existence of the new user by running:

.. literalinclude:: ../code/internal-user/task.yaml
    :language: bash
    :start-after: [docs:check-user]
    :end-before: [docs:check-user-end]
    :dedent: 2
