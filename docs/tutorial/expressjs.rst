.. _build-a-rock-for-an-expressjs-application:

Build a rock for an Express application
---------------------------------------

In this tutorial, we'll containerise a simple Express application into a rock
using Rockcraft's ``expressjs-framework`` :ref:`extension
<expressjs-framework-reference>`.

It should take 25 minutes for you to complete.

You won’t need to come prepared with intricate knowledge of software
packaging, but familiarity with Linux paradigms, terminal operations,
and Express is required.

Once you complete this tutorial, you’ll have a working rock for an Express
application. You’ll gain familiarity with Rockcraft and the
``expressjs-framework`` extension, and have the experience to create
rocks for Express applications.

Setup
=====

.. include:: /reuse/tutorial/setup_edge.rst

This tutorial requires the ``latest/edge`` channel of Rockcraft. Run
``sudo snap refresh rockcraft --channel latest/edge`` to get the latest
edge version.

In order to test the Express application locally, before packing it into a
rock, install ``npm`` and initialize the starter app.

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:install-deps]
    :end-before: [docs:install-deps-end]
    :dedent: 2


Create the Express application
==============================

Start by creating the "Hello, world" Express application that we'll pack in
this tutorial.

Create an empty project directory:

.. code-block:: bash

   mkdir expressjs-hello-world
   cd expressjs-hello-world

Next, create a skeleton for the project with the Express application generator:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:init-app]
    :end-before: [docs:init-app-end]
    :dedent: 2

Let's Run the Express application to verify that it works:

.. code:: bash

  npm start

The application starts an HTTP server listening on port 3000
that we can test by using curl to send a request to the root
endpoint. We may need a new terminal for this -- if using Multipass, run
``multipass shell rock-dev`` to get another terminal:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:curl-expressjs]
    :end-before: [docs:curl-expressjs-end]
    :dedent: 2

The Express application should respond with *Welcome to Express* web page.

.. note::
    The response from the Express application includes HTML and CSS which
    makes it difficult to read on a terminal. Visit ``http://localhost:3000``
    using a browser to see the fully rendered page.

The Express application looks good, so let's stop it for now
with :kbd:`Ctrl` + :kbd:`C`, then move out of the application directory
``cd ..``.

Pack the Express application into a rock
========================================

First, we'll need a ``rockcraft.yaml`` project file. Rockcraft will automate its
creation and tailor it for a Express application when we tell it to use the
``expressjs-framework`` profile:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

Open ``rockcraft.yaml`` in a text editor and check that the ``name``
key is set to ``expressjs-hello-world``. Ensure that ``platforms`` includes
the architecture of the host. For example, if the host uses the ARM
architecture, include ``arm64`` in ``platforms``.

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
application:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use the same curl command as before to send a request to the Express
application's root endpoint which is running inside the container:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:curl-expressjs-rock]
    :end-before: [docs:curl-expressjs-rock-end]
    :dedent: 2

The Express application again responds with *Welcome to Express* page.

View the application logs
~~~~~~~~~~~~~~~~~~~~~~~~~

When deploying the Express rock, we can always get the application logs with
:ref:`pebble_explanation_page`:

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


Stop the application
~~~~~~~~~~~~~~~~~~~~

Now we have a fully functional rock for a Express application! This concludes
the first part of this tutorial, so we'll stop the container and remove the
respective image for now:

.. literalinclude:: code/expressjs/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2


Update the Express application
==============================

For our final task, let's update our application. As an example,
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

Since we are creating a new version of the application, set
``version: '0.2'`` in the project file.
The top of the ``rockcraft.yaml`` file should look similar to the following:

.. code-block:: yaml
    :caption: ~/expressjs-hello-world/rockcraft.yaml
    :emphasize-lines: 6

    name: expressjs-hello-world
    # see https://documentation.ubuntu.com/rockcraft/en/latest/explanation/bases/
    # for more information about bases and using 'bare' bases for chiselled rocks
    base: bare # as an alternative, a ubuntu base can be used
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

The updated application should respond with the current date and time (e.g.
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

.. collapse:: If using Multipass...

    If we created an instance using Multipass, we can also clean it up.
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

* :ref:`Rockcraft tutorials<tutorial>`.
* :ref:`expressjs-framework reference<expressjs-framework-reference>`.
* :ref:`why_use_rockcraft`.
* :ref:`What is a Rock?<rocks_explanation>`.

----

.. _troubleshooting-expressjs:

Troubleshooting
===============

**Application updates not taking effect?**

Upon changing the Express application and re-packing the rock, if
the changes are not taking effect, try running ``rockcraft clean`` and pack
the rock again with ``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/install-multipass
