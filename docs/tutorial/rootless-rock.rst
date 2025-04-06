Create a rootless rock
**********************

Project setup
-------------

In the previous step we created a baseless rock that
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

.. tabs::

    .. group-tab:: Using run-user

        The ``run-user`` directive currently supports the ``_daemon_`` user. This way,
        we can set that value in our ``rockcraft.yaml``:

        .. literalinclude:: code/rootless-rock/rockcraft-run-user.yaml
            :caption: rockcraft.yaml
            :language: yaml

        Note that even if we set the ``run-user`` field, we still need to set the
        permissions for the files that are accessed by ``nginx``. To do that, we
        use the ``chown`` command in the ``override-prime`` section.

        You can use tools like `dive`_ to inspect the contents and permissions of
        each layer:

        .. code-block:: text

            ┃ ● Current Layer Contents ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            Permission     UID:GID       Size  Filetree
            rwxr-xr-x          0:0      245 B  ├── .rock
            -rw-r--r--         0:0      245 B  │   └── metadata.yaml
            drwxr-xr-x         0:0      24 kB  ├── etc
            -rw-r--r--         0:0      453 B  │   ├── group
            drwxr-xr-x         0:0      329 B  │   ├─⊕ logrotate.d
            drwxr-xr-x 584792:584792    22 kB  │   ├─⊕ nginx
            -rw-r--r--         0:0      904 B  │   └── passwd
            drwxr-xr-x         0:0        0 B  ├── home
            -rwxrwxrwx         0:0        0 B  ├── lib → usr/lib
            -rwxrwxrwx         0:0        0 B  ├── lib64 → usr/lib64
            -rw-rw-r--         0:0      999 B  ├── rockcraft-new-user.yaml
            -rw-rw-r--         0:0      878 B  ├── rockcraft-run-user.yaml
            -rw-rw-r--         0:0      878 B  ├── rockcraft.yaml
            drwx------         0:0        0 B  ├── root
            drwxr-xr-x 584792:584792      0 B  ├── run
            -rw-rw-r--         0:0     1.7 kB  ├── task.yaml
            drwxr-xr-x         0:0      22 MB  ├─⊕ usr
            drwxr-xr-x         0:0      317 B  └── var
            drwxr-xr-x         0:0        0 B      ├── cache
            drwxr-xr-x         0:0      179 B      ├── lib
            drwxr-xr-x 584792:5847        0 B      │   ├── nginx
            drwxr-xr-x         0:0      179 B      │   └─⊕ pebble
            drwxr-xr-x         0:0        0 B      ├─⊕ log
            -rwxrwxrwx         0:0        0 B      ├── run → ../run
            drwxrwxrwx         0:0        0 B      ├── tmp
            drwxr-xr-x         0:0      138 B      └── www
            drwxr-xr-x 584792:584792    138 B          └── html
            -rw-rw-r-- 584792:584792    138 B              └── index.html

        As you can see, the ``_daemon_`` user owns the files required for nginx
        to run, without extra root privileges.

    .. group-tab:: Manually adding user and group

        If we want to manually add a new user, we can use the ``override-prime``
        directive to run a set of commands during the prime step, which is the
        last one in the lifecycle.

        Additionally, we will set the ``user`` field of the service so the
        nginx service run with that user.

        .. literalinclude:: code/rootless-rock/rockcraft-new-user.yaml
            :caption: rockcraft.yaml
            :language: yaml

        You can use tools like `dive`_ to inspect the contents and permissions of
        each layer:

        .. code-block:: text

            ┃ ● Current Layer Contents ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            Permission     UID:GID       Size  Filetree
            rwxr-xr-x          0:0      245 B  ├── .rock
            -rw-r--r--         0:0      245 B  │   └── metadata.yaml
            drwxr-xr-x         0:0      24 kB  ├── etc
            -rw-r--r--         0:0      453 B  │   ├── group
            drwxr-xr-x         0:0      329 B  │   ├─⊕ logrotate.d
            drwxr-xr-x     4242:4242    22 kB  │   ├─⊕ nginx
            -rw-r--r--         0:0      904 B  │   └── passwd
            drwxr-xr-x         0:0        0 B  ├── home
            -rwxrwxrwx         0:0        0 B  ├── lib → usr/lib
            -rwxrwxrwx         0:0        0 B  ├── lib64 → usr/lib64
            -rw-rw-r--         0:0      999 B  ├── rockcraft-new-user.yaml
            -rw-rw-r--         0:0      878 B  ├── rockcraft-run-user.yaml
            -rw-rw-r--         0:0      878 B  ├── rockcraft.yaml
            drwx------         0:0        0 B  ├── root
            drwxr-xr-x     4242:4242      0 B  ├── run
            -rw-rw-r--         0:0     1.7 kB  ├── task.yaml
            drwxr-xr-x         0:0      22 MB  ├─⊕ usr
            drwxr-xr-x         0:0      317 B  └── var
            drwxr-xr-x         0:0        0 B      ├── cache
            drwxr-xr-x         0:0      179 B      ├── lib
            drwxr-xr-x     4242:4242      0 B      │   ├── nginx
            drwxr-xr-x         0:0      179 B      │   └─⊕ pebble
            drwxr-xr-x         0:0        0 B      ├─⊕ log
            -rwxrwxrwx         0:0        0 B      ├── run → ../run
            drwxrwxrwx         0:0        0 B      ├── tmp
            drwxr-xr-x         0:0      138 B      └── www
            drwxr-xr-x      4242:4242   138 B          └── html
            -rw-rw-r--      4242:4242   138 B              └── index.html

        As you can see, the new ``nginx`` user owns the files required for
        ``nginx`` to run, without extra root privileges.


Pack the rock with Rockcraft
----------------------------

Once everything is set up, we just need to pack the rock with rockcraft
and copy it to the docker daemon to use it later on:

.. literalinclude:: code/rootless-rock/task.yaml
    :language: bash
    :start-after: [docs:build-and-copy-rock]
    :end-before: [docs:build-and-copy-rock-end]
    :dedent: 2

Run the rock with docker
------------------------

Once packed and copied you can now run the rock using docker. Note that
you will need to bind the ports to access the page via HTTP:

.. literalinclude:: code/rootless-rock/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Once the container is running (you can check with ``docker ps``) you should
be able to see the HTML page in your browser, or using curl:

.. literalinclude:: code/rootless-rock/task.yaml
    :language: bash
    :start-after: [docs:test-rock]
    :end-before: [docs:test-rock-end]
    :dedent: 2

The output should be the contents of ``index.html``:

.. literalinclude:: code/rootless-rock/index.html
    :language: text


.. _dive: https://github.com/wagoodman/dive
