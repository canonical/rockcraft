.. _tutorial-build-a-rock-for-an-express-app:

Build a rock for an Express app
-------------------------------

In this tutorial, we'll containerise a simple Express app into a rock
using Rockcraft's ``expressjs-framework`` :ref:`extension
<reference-express-framework>`.

It should take 25 minutes for you to complete.

You won’t need to come prepared with intricate knowledge of software
packaging, but familiarity with Linux paradigms, terminal operations,
and Express is required.

Once you complete this tutorial, you’ll have a working rock for an Express
app. You’ll gain familiarity with Rockcraft and the
``expressjs-framework`` extension, and have the experience to create
rocks for Express apps.

Setup
=====

.. include:: /reuse/tutorial/setup_edge.rst

This tutorial requires the ``latest/edge`` channel of Rockcraft. Run
``sudo snap refresh rockcraft --channel latest/edge`` to get the latest
edge version.

In order to test the Express app locally, before packing it into a
rock, install NPM and initialize the starter app.

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:install-deps]
    :end-before: [docs:install-deps-end]
    :dedent: 2


Create the Express app
======================

Start by creating the "Hello, world" Express app that we'll pack in
this tutorial.

Create an empty project directory:

.. code-block:: bash

   mkdir expressjs-hello-world
   cd expressjs-hello-world

Next, create a skeleton for the project with the Express app generator:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:init-app]
    :end-before: [docs:init-app-end]
    :dedent: 2

Let's run the Express app to verify that it works:

.. code:: bash

  npm start

The app starts an HTTP server listening on port 3000
that we can test by using curl to send a request to the root
endpoint. We'll need a new shell of the VM for this -- in a separate terminal,
run ``multipass shell rock-dev`` again:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:curl-expressjs]
    :end-before: [docs:curl-expressjs-end]
    :dedent: 2

The Express app should respond with *Welcome to Express* web page.

.. note::
    The response from the Express app includes HTML and CSS which
    makes it difficult to read on a terminal. Visit
    ``http://<Multipass private IP>:3000`` using a browser to see the fully
    rendered page, replacing ``<Multipass private IP>`` with your VM's
    private IP address. To determine the IP address of your VM, outside of the
    VM, run:

    .. code-block:: bash

        multipass info rock-dev | grep IP

The Express app looks good, so let's close the terminal instance we used for
testing and stop the app in the original terminal instance by pressing
:kbd:`Ctrl` + :kbd:`C`.

Pack the Express app into a rock
================================

Now let's create a container image for our Express app. We'll use a rock,
which is an OCI-compliant container image based on Ubuntu.

First, we'll need a ``rockcraft.yaml`` project file. We'll take advantage of a
pre-defined extension in Rockcraft with the ``--profile`` flag that caters
initial rock files for specific web app frameworks. Using the
Express profile, Rockcraft automates the creation of
``rockcraft.yaml`` and tailors the file for an Express app.
From the ``~/expressjs-hello-world`` directory, initialize the rock:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

The ``rockcraft.yaml`` file will automatically be created and set the name
based on your working directory.

Check out the contents of ``rockcraft.yaml``:

.. code-block:: bash

    cat rockcraft.yaml

The top of the file should look similar to the following snippet:

.. code-block:: yaml
    :caption: ~/expressjs-hello-world/rockcraft.yaml

    name: expressjs-hello-world
    # see https://documentation.ubuntu.com/rockcraft/latest/explanation/bases/
    # for more information about bases and using 'bare' bases for chiselled rocks
    base: bare # as an alternative, an ubuntu base can be used
    build-base: ubuntu@24.04 # build-base is required when the base is bare
    version: '0.1' # just for humans. Semantic versioning is recommended
    summary: A summary of your ExpressJS app # 79 char long summary
    description: |
        This is expressjs-hello-world's description. You have a paragraph or two to tell the
        most important story about it. Keep it under 100 words though,
        we live in tweetspace and your description wants to look good in the
        container registries out there.
    # the platforms this rock should be built on and run on.
    # you can check your architecture with `dpkg --print-architecture`
    platforms:
        amd64:
        # arm64:
        # ppc64el:
        # s390x:

    ...

Verify that the ``name`` is ``expressjs-hello-world``.

Ensure that ``platforms`` includes the architecture of your host. Check
the architecture of your system:

.. code-block:: bash

    dpkg --print-architecture


Edit the ``platforms`` key in ``rockcraft.yaml`` if required.

As the ``expressjs-framework`` extension is still experimental, export the
environment variable ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS``:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:experimental]
    :end-before: [docs:experimental-end]
    :dedent: 2

Pack the rock:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

.. warning::
   There is a `known connectivity issue with LXD and Docker
   <lxd-docker-connectivity-issue_>`_. If we see a
   networking issue such as "*A network related operation failed in a context
   of no network access*" or ``Client.Timeout``, we need to allow egress network
   traffic to flow from the managed LXD bridge.

   First, run ``lxc network list`` to show the available networks. The
   bridge will have ``TYPE: bridge`` and ``MANAGED: YES``. Save the name to an
   environment variable:

   .. code-block::

       NETWORK_BRIDGE=<name of managed LXD bridge>

   Then, update the network traffic flow using:

   .. code-block::

       sudo iptables  -I DOCKER-USER -i $NETWORK_BRIDGE -j ACCEPT
       sudo ip6tables -I DOCKER-USER -i $NETWORK_BRIDGE -j ACCEPT
       sudo iptables  -I DOCKER-USER -o $NETWORK_BRIDGE -m conntrack \
         --ctstate RELATED,ESTABLISHED -j ACCEPT
       sudo ip6tables -I DOCKER-USER -o $NETWORK_BRIDGE -m conntrack \
         --ctstate RELATED,ESTABLISHED -j ACCEPT

Depending on the network, this step can take a couple of minutes to finish.

Once Rockcraft has finished packing the Express rock, we'll find a new file in
the working directory (an `OCI <OCI_image_spec_>`_ image) with the ``.rock``
extension:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2


Run the Express rock with Docker
================================

We already have the rock as an OCI image. Now we
need to load it into Docker. Docker requires rocks to be imported into the
daemon since they can't be run directly like an executable.

Copy the rock:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

This command contains the following pieces:

- ``--insecure-policy``: adopts a permissive policy that
  removes the need for a dedicated policy file.
- ``oci-archive``: specifies the rock we created for our Express app.
- ``docker-daemon``: specifies the name of the image in the Docker registry.

Check that the image was successfully loaded into Docker:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:docker-images]
    :end-before: [docs:docker-images-end]
    :dedent: 2

The output should list the Express image, along with its tag, ID and
size:

.. terminal::

    REPOSITORY              TAG       IMAGE ID       CREATED       SIZE
    expressjs-hello-world   0.1       30c7e5aed202   2 weeks ago   304MB

Now we're finally ready to run the rock and test the containerised Express
app:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use the same curl command as before to send a request to the Express
app's root endpoint which is running inside the container:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:curl-expressjs-rock]
    :end-before: [docs:curl-expressjs-rock-end]
    :dedent: 2

The Express app again responds with *Welcome to Express* page.

View the app logs
~~~~~~~~~~~~~~~~~

When deploying the Express rock, we can always get the app logs with
:ref:`explanation-pebble`:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:get-logs]
    :end-before: [docs:get-logs-end]
    :dedent: 2

As a result, Pebble will give us the logs for the
``expressjs`` service running inside the container.
We should expect to see something similar to this:

.. terminal::

    app@0.0.0 start
    node ./bin/www
    GET / 200 62.934 ms - 170

We can also choose to follow the logs by using the ``-f`` option with the
``pebble logs`` command above. To stop following the logs, press :kbd:`Ctrl` +
:kbd:`C`.


Stop the app
~~~~~~~~~~~~

Now we have a fully functional rock for a Express app! This concludes
the first part of this tutorial, so we'll stop the container and remove the
respective image for now:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2


Update the Express app
======================

For our final task, let's update our app. As an example,
let's add a new ``/time`` endpoint that returns the current time.

Start by creating the ``app/routes/time.js`` file in a text editor and paste the
code from the snippet below:

.. literalinclude:: code/expressjs/time.js
    :caption: ~/expressjs-hello-world/app/routes/time.js
    :language: javascript

Place the code snippet below in ``app/app.js`` under routes registration section
along with other ``app.use(...)`` lines.
It will register the new ``/time`` endpoint:

.. literalinclude:: code/expressjs/time_app.js
    :caption: ~/expressjs-hello-world/app/app.js
    :language: javascript
    :start-after: [docs:append-lines]
    :end-before: [docs:append-lines-end]

Since we are creating a new version of the app, set
``version: '0.2'`` in the project file.
The top of the ``rockcraft.yaml`` file should look similar to the following:

.. code-block:: yaml
    :caption: ~/expressjs-hello-world/rockcraft.yaml
    :emphasize-lines: 6

    name: expressjs-hello-world
    # see https://documentation.ubuntu.com/rockcraft/latest/explanation/bases/
    # for more information about bases and using 'bare' bases for chiselled rocks
    base: bare # as an alternative, an ubuntu base can be used
    build-base: ubuntu@24.04 # build-base is required when the base is bare
    version: '0.2'
    summary: A summary of your ExpressJS app # 79 char long summary
    description: |
        This is expressjs-hello-world's description. You have a paragraph or two to tell the
        most important story about it. Keep it under 100 words though,
        we live in tweetspace and your description wants to look good in the
        container registries out there.
    # the platforms this rock should be built on and run on.
    # you can check your architecture with `dpkg --print-architecture`
    platforms:
        amd64:
        # arm64:
        # ppc64el:
        # s390x:

.. note::

    If we repack the rock without changing the version, the new rock will have the
    same name and overwrite the last one we built. It's a good practice to change
    the version whenever we make changes to the app in the image.

Pack and run the rock using similar commands as before:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:docker-run-update]
    :end-before: [docs:docker-run-update-end]
    :dedent: 2

The resulting ``.rock`` file will be named differently, as
its new version will be part of the filename.

Finally, use curl to send a request to the ``/time`` endpoint:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:curl-time]
    :end-before: [docs:curl-time-end]
    :dedent: 2

The updated app should respond with the current date and time (e.g.
``Fri Jan 10 2025 03:11:44 GMT+0000 (Coordinated Universal Time)``).

.. tip::

    If you are getting a ``404`` for the ``/time`` endpoint, check the
    :ref:`troubleshooting-expressjs` steps below.

Final Cleanup
~~~~~~~~~~~~~

We can now stop the container and remove the corresponding image:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-updated]
    :end-before: [docs:stop-docker-updated-end]
    :dedent: 2

Reset the environment
=====================

We've reached the end of this tutorial.

If we'd like to reset the working environment, we can simply run the
following:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:cleanup]
    :end-before: [docs:cleanup-end]
    :dedent: 2

We can also clean the Multipass instance up.
Start by exiting it:

.. code-block:: bash

    exit

And then we can proceed with its deletion:

.. code-block:: bash

    multipass delete rock-dev
    multipass purge

----

Next steps
==========

Congratulations! You've reached the end of this tutorial. You created a
Express app, packaged it into a rock, and practiced some typical development skills
such as viewing logs and updating the app.

But there is a lot more to explore:

.. list-table::
    :widths: 30 30
    :header-rows: 1

    * - If you are wondering...
      - Visit...
    * - "What's next?"
      - :external+charmcraft:ref:`Write your first Kubernetes charm for an Express app
        in Charmcraft <write-your-first-kubernetes-charm-for-a-expressjs-app>`
    * - "How do I...?"
      - :ref:`how-to-manage-a-12-factor-app-rock`
    * - "How do I get in touch?"
      - `Matrix channel <https://matrix.to/#/#12-factor-charms:ubuntu.com>`_
    * - "What is...?"
      - :ref:`expressjs-framework extension <reference-express-framework>`

        :ref:`What is a Rock? <explanation-rocks>`
    * - "Why...?", "So what?"
      - :external+12-factor:ref:`12-Factor app principles and support in Charmcraft
        and Rockcraft <explanation>`

----

.. _troubleshooting-expressjs:

Troubleshooting
===============

**App updates not taking effect?**

Upon changing the Express app and re-packing the rock, if
the changes are not taking effect, try running ``rockcraft clean`` and pack
the rock again with ``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/install-multipass
