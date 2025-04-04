Create a rootless rock
**********************

Project setup
-------------

In the previous section we created a baseless rock that
served an ``index.html`` page with Nginx slices. This rock
is inherently lighter and less vulnerable than its
non-chiselled version. However, it is still running as ``root``,
which not only is a bad practice, but a security risk.

To fix that, we will take that rock and turn it into a
"rootless" root by declaring a new user that will run the
``nginx`` service, instead of ``root``. We should have these
files at this point:

.. code-block:: text

    .
    ├─ rockcraft.yaml
    ├─ nginx.conf
    └─ index.html

    3 files

Different approaches
--------------------

A rootless rock does not require root privileges to be run, this means that ``root``
does not exist in this context and a new user is be created without such privileges.
There are two approaches when it comes to adding a new internal user to a rock,
depending on the situation you may want to:

- Use run-user:
    The :ref:`run-user <rockcraft_yaml_run_user>` field can be used
    in the rock's project file to specify the user that will run its services with.
    However, the ``run-user`` key only accepts a limited number of users, which could
    be a constraint for certain container applications, in which case we would need to
    take the second approach.

- Manually add a new user and group:
    In cases where the service running
    inside the rock is required to run with a specific user the build
    step must be overriden in the rock's project file to invoke ``useradd`` and
    ``groupadd`` commands.

In any case, to add a new internal user or group to a rock, these slices are needed:

- ``base-files_home``: to create the base folders such as ``/root`` and ``/home``,
- ``base-passwd_data``: to produce ``/etc/passwd`` and ``/etc/group`` files.

In our case, both slices were already included in the previous section.

Create a new user in the rock
-----------------------------

Lets show how this can be achieved following both approaches:


