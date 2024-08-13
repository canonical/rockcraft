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
    :start-after: [docs:rock-build]
    :end-before: [docs:rock-build-end]

For an example of how to access the user inside the rock, here's a simple
Node.js web service. This web service will also print out a message that
contains the user that is running the service. To create the files necessary
for this service, create a folder called ``src`` and file called ``server.js``
in it with the following contents:

.. literalinclude:: ../code/internal-user/src/server.js
    :language: javascript

You will also need a ``package.json`` file in the same folder to define the
project name and the command that will run the ``server.js`` script:

.. literalinclude:: ../code/internal-user/src/package.json
    :language: javascript

Then, add a service to  ``rockcraft.yaml`` that runs the web service:

.. literalinclude:: ../code/internal-user/rockcraft.yaml
    :language: yaml
    :start-after: [docs:rock-services]
    :end-before: [docs:rock-services-end]

Next, we will use the ``npm`` plugin to build our Node.js project within the
rock, similarly to what we have done in the
:ref:`Bundle a Node.js app within a rock <bundle_a_nodejs_app_within_a_rock>`
tutorial. The final ``rockcraft.yaml`` file will look like this:

.. literalinclude:: ../code/internal-user/rockcraft.yaml
    :language: yaml

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
image container:

.. literalinclude:: ../code/internal-user/task.yaml
    :language: bash
    :start-after: [docs:check-user]
    :end-before: [docs:check-user-end]
    :dedent: 2

The response should contain the new user name:

.. code-block::

    Serving by myuser on port 8080
