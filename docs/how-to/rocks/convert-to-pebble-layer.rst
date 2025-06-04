How to convert an entrypoint to a Pebble layer
***********************************************

This guide will show you how to take an existing Docker image entrypoint
and convert it into a Pebble layer, aka the list of one or more services
which is defined in the project file and then taken by the rock's
Pebble entrypoint.


Reference entrypoint
--------------------

For this guide, the reference Docker image entrypoint will be NGINX. The
official Debian-based NGINX image's Dockerfile can be found `here
<https://github.com/nginxinc/docker-nginx/blob/
73a5acae6945b75b433cafd0c9318e4378e72cbb/mainline/debian/Dockerfile>`_.

In summary, this Dockerfile is basically installing NGINX into the image and
then defining the OCI entrypoint to be a custom `shell script
<https://github.com/nginxinc/docker-nginx/blob/
73a5acae6945b75b433cafd0c9318e4378e72cbb/mainline/debian/docker-entrypoint.sh>`_
which parses the first argument given to it at container deployment time,
and then configures and launches NGINX accordingly.

Design the Pebble services
--------------------------

A `Pebble layer
<https://canonical-pebble.readthedocs-hosted.com/en/latest/reference/
layer-specification/>`_
is composed of metadata, checks and services. The latter is present in
the project file as a `top-level key
<https://canonical-rockcraft.readthedocs-hosted.com/en/latest/reference/
rockcraft.yaml/#format-specification>`_
and it represents the services which are loaded by the Pebble entrypoint when
deploying a rock.

Given the reference entrypoint, this guide's goal is to create two services:
one for ``nginx`` and another for ``nginx-debug``. The following ``services``
snippet does just that:

.. literalinclude:: ../code/convert-to-pebble-layer/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml
    :start-after: Pebble entrypoint

This is defining two separate Pebble services which are disabled by default
at startup, have the same environment variable, but are executed with
different commands (``nginx`` and ``nginx-debug``).

Build the rock
--------------

Copy the above snippet and incorporate it into the project file
which will be used to build your rock, as shown below:

.. literalinclude:: ../code/convert-to-pebble-layer/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

This project file is almost fully declarative, with the creation of the
"nginx" user being the only scripted step.

To reproduce what the reference NGINX Dockerfile is doing, notice the use of
``package-repositories`` in this project file, allowing you to also
make use of NGINX's 3rd party package repository (even using the same
GPG key ID as the one used in `the Dockerfile
<https://github.com/nginxinc/docker-nginx/blob/
73a5acae6945b75b433cafd0c9318e4378e72cbb/mainline/debian/Dockerfile>`_).

**NOTE**: to add custom configuration files, you can use the ``dump`` plugin.

Now, build the final custom NGINX rock with:

.. literalinclude:: ../code/convert-to-pebble-layer/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

You should see something like this:

..  code-block:: text
    :emphasize-lines: 5,26
    :class: log-snippets

    Launching instance...
    Retrieved base ubuntu@22.04 for amd64
    Extracted ubuntu@22.04
    Refreshing repositories | (4.6s)
    Package repositories installed
    Executed: pull nginx-user
    Executed: pull nginx
    Executed: pull pebble
    Executed: overlay nginx-user
    Executed: overlay nginx
    Executed: overlay pebble
    Executed: build nginx-user
    Executed: skip pull nginx-user (already ran)
    Executed: skip overlay nginx-user (already ran)
    Executed: skip build nginx-user (already ran)
    Executed: stage nginx-user (required to build 'nginx')
    Executed: build nginx
    Executed: build pebble
    Executed: skip stage nginx-user (already ran)
    Executed: stage nginx
    Executed: stage pebble
    Executed: prime nginx-user
    Executed: prime nginx
    Executed: prime pebble
    Executed parts lifecycle
    Exported to OCI archive 'custom-nginx-rock_latest_amd64.rock'

Then run the rock:

.. tabs::

    .. group-tab:: Docker

        Copy the resulting rock (from the OCI archive format) to the Docker daemon
        via:

        .. literalinclude:: ../code/convert-to-pebble-layer/task.yaml
            :language: bash
            :start-after: [docs:skopeo]
            :end-before: [docs:skopeo-end]
            :dedent: 2

        And finally, run the container:

        .. literalinclude:: ../code/convert-to-pebble-layer/task.yaml
            :language: bash
            :start-after: [docs:docker-run]
            :end-before: [docs:docker-run-end]
            :dedent: 2

        The Pebble daemon will start without any NGINX service, although you could
        still later on ask for either service to be started. For instance, you can
        start the ``nginx`` service by typing:

        .. literalinclude:: ../code/convert-to-pebble-layer/task.yaml
            :language: bash
            :start-after: [docs:service-start]
            :end-before: [docs:service-start-end]
            :dedent: 2

    .. group-tab:: Podman

        Run the container with podman:

        .. literalinclude:: ../code/convert-to-pebble-layer/task.yaml
            :language: bash
            :start-after: [docs:podman-run]
            :end-before: [docs:podman-run-end]
            :dedent: 2

        The Pebble daemon will start without any NGINX service, although you could
        still later on ask for either service to be started. For instance, you can
        start the ``nginx`` service by typing:

        .. literalinclude:: ../code/convert-to-pebble-layer/task.yaml
            :language: bash
            :start-after: [docs:service-start-podman]
            :end-before: [docs:service-start-podman-end]
            :dedent: 2

We could have chosen to make one of the two services run on startup by setting
its corresponding ``startup`` key to ``enabled``.

Once you start one of the services, your container should be deployed and
running the ``nginx`` or ``nginx-debug`` service, and you should be able to see
the NGINX landing page by accessing port 8080 on you localhost:

.. literalinclude:: ../code/convert-to-pebble-layer/task.yaml
    :language: bash
    :start-after: [docs:curl]
    :end-before: [docs:curl-end]
    :dedent: 2

For which you should see the following output:

..  code-block:: text
    :emphasize-lines: 4
    :class: log-snippets

    <!DOCTYPE html>
    <html>
    <head>
    <title>Welcome to nginx!</title>
    <style>
    html { color-scheme: light dark; }
    body { width: 35em; margin: 0 auto;
    font-family: Tahoma, Verdana, Arial, sans-serif; }
    </style>
    </head>
    <body>
    <h1>Welcome to nginx!</h1>
    <p>If you see this page, the nginx web server is successfully installed and
    working. Further configuration is required.</p>

    <p>For online documentation and support please refer to
    <a href="http://nginx.org/">nginx.org</a>.<br/>
    Commercial support is available at
    <a href="http://nginx.com/">nginx.com</a>.</p>

    <p><em>Thank you for using nginx.</em></p>
    </body>
    </html>
