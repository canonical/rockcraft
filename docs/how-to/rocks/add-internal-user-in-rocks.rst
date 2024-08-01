.. _add_internal_user_in_rocks:

How to add an internal user to a rock
*************************************

Rockcraft allows you to use ``run-user`` to specify the user you want to run
the rock's service(s) with. Without using that field in your rockcraft.yaml,
the service(s) will be run by the root user. The downside, however, of using
``run-user`` is that it only supports one user called ``_daemon_`` with a
UID/GID of 84792. For most daemon services that's sufficient, but other
services require that the running user should have a specific username and/or
UID.

In order to add a new internal user or group to a rock, two packages (or their
respective slices) are needed:
- ``base-files``: to create the base dirs such as ``/root`` and ``/home``,
- ``base-passwd``: to produce basic ``/etc/passwd`` and ``/etc/group`` files.

Invoking the ``useradd`` and ``groupadd`` commands can take place in the
:ref:`build <lifecycle>` step, by appending the commands to the build flow.
However, the changes made by those commands normally apply to the base system,
not the build system. Hence, ``$CRAFT_PART_INSTALL`` should be passed as the
root directory to those two commands.

The following *rockcraft.yaml* illustrates how to use ``useradd`` command in
``override-build`` field inside a part.

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
