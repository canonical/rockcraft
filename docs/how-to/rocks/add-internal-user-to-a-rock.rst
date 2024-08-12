.. _add_internal_user_to_a_rock:

How to add an new internal user to a rock
*****************************************

You can declare :ref:`run-user <rockcraft_yaml_run_user>` in ``rockcraft.yaml``
to specify which user you want to run a rock's services with. If you don't
specify a user, the services run as root by default. The ``run-user`` key
only accepts a limited number of users, which could be a constraint for certain
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
``override-build`` field. However, the changes made by those commands will be
only applied on the build instance, and will not be available in the resulting
rock. Hence, ``$CRAFT_PART_INSTALL`` should be passed as the root directory to
those two commands.

A full example
--------------

The following ``rockcraft.yaml`` illustrates how to use the ``useradd`` command
in the ``override-build`` field inside a part.

.. literalinclude:: ../code/internal-user/rockcraft.yaml
    :language: yaml
    :start-after: [docs:rock-parts]
    :end-before: [docs:rock-parts-end]

Next, let's add a simple Python web service that runs a python script. The
python script will be executed to return an HTTP response containing the
username that is running the python web service. We will put this file in a
``cgi-bin`` folder, and give the file the executive permission with
``chmod +x cgi-bin/getuser.py``:
For an example of how to access the user inside the rock, here's a simple
Python web service that runs a script. The script will return an HTTP response
containing the user that is running the web service:

.. literalinclude:: ../code/internal-user/cgi-bin/getuser.py
    :language: python

Inside the ``override-build`` field, copy the ``cgi-bin`` folder to the part's
installation folder ``$CRAFT_PART_INSTALL``, and give execute permission to the
Python script file ``getuser.py``.

.. code-block::

    cp -r cgi-bin/ ${CRAFT_PART_INSTALL}/
    chmod +x ${CRAFT_PART_INSTALL}/cgi-bin/getuser.py

Then, add a service to  ``rockcraft.yaml`` that runs the web service with
``cgi`` capabilities:

.. literalinclude:: ../code/internal-user/rockcraft.yaml
    :language: yaml
    :start-after: [docs:rock-services]
    :end-before: [docs:rock-services-end]

With the user and web service in place, build the rock:

.. literalinclude:: ../code/internal-user/task.yaml
    :language: bash
    :start-after: [docs:pack-rock]
    :end-before: [docs:pack-rock-end]
    :dedent: 2

Next, we will convert the rock from an OCI archive to a Docker image using
skopeo:

.. literalinclude:: ../code/internal-user/task.yaml
    :language: bash
    :start-after: [docs:skopeo]
    :end-before: [docs:skopeo-end]
    :dedent: 2

You can now check which internal user is running the service by running the
image and querying ``http://127.0.0.1/cgi-bin/getuser.py`` with curl:

.. literalinclude:: ../code/internal-user/task.yaml
    :language: bash
    :start-after: [docs:check-user]
    :end-before: [docs:check-user-end]
    :dedent: 2

The response should contain the new user name:

.. code-block::

    myuser
