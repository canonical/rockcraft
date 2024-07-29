.. _add_internal_user_in_rocks:

How to add an internal user to a rock
*************************************

Rockcraft allows you to use ``run-user`` to specify the user you want to the
rock's service(s) with. Without using that field in your rockcraft.yaml, the
service(s) will be run by the root user. The downside, however, of using
``run-user`` is that only supports one user called ``_daemon_`` with a UID/GID
of 84792. For some daemon services that will be enough, but some other services
require that the running user should have a specific username and/or UID.

In order to add new internal user or group to a rock, three packages (or their
respective slices) are needed:
- ``base-files``: to create the base directories such as ``/etc`` and ``/bin``
- ``base-passwd``: to produce basic ``/etc/passwd`` and ``/etc/group`` files,
- ``passwd``: to provide ``useradd`` and ``groupadd`` commands.

Invoking ``useradd`` and ``groupadd`` command can take place in the
:ref:`build <lifecycle>` step, by appending the commands to the build flow.
However, the changes made by those commands should apply to the base system and
not the build system. Hence, ``$CRAFT_PART_INSTALL`` should be passed as the
root system to those two commands.

The following *rockcraft.yaml* illustrates how to use ``useradd`` command in
``override-build`` field.

.. literalinclude:: ../code/internal-user/rockcraft.yaml
    :language: yaml

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
