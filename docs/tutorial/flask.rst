.. _build-a-rock-for-a-flask-application:

Build a rock for a Flask application
------------------------------------

In this tutorial, we'll create a simple Flask application and learn how to
containerise it in a rock, using Rockcraft's ``flask-framework``
:ref:`extension <flask-framework-reference>`.

Setup
=====

.. include:: /reuse/tutorial/setup.rst

.. note::
    This tutorial requires version ``1.5.2`` or later for Rockcraft. Check
    your version using ``rockcraft --version``. If you have an older version
    of Rockcraft installed, use
    ``sudo snap refresh rockcraft --channel latest/stable`` to get the latest
    stable version.

Finally, create a new directory for this tutorial and go inside it:

.. code-block:: bash

   mkdir flask-hello-world
   cd flask-hello-world

Create the Flask application
============================

Start by creating the "Hello, world" Flask application that will be used for
this tutorial.

Create a ``requirements.txt`` file, copy the following text into it and then
save it:

.. literalinclude:: code/flask/requirements.txt

In order to test the Flask application locally (before packing it into a rock),
install ``python3-venv`` and create a virtual environment:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:create-venv]
    :end-before: [docs:create-venv-end]
    :dedent: 2

In the same directory, copy and save the following into a text file called
``app.py``:

.. literalinclude:: code/flask/app.py
    :language: python

Run the Flask application using ``flask run -p 8000`` to verify that it works.

Test the Flask application by using ``curl`` to send a request to the root
endpoint. You may need a new terminal for this, if you are using Multipass use
``multipass shell rock-dev`` to get another terminal:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:curl-flask]
    :end-before: [docs:curl-flask-end]
    :dedent: 2

The Flask application should respond with ``Hello, world!``.

The Flask application looks good, so stop it for now using ``ctrl + c``.

Pack the Flask application into a rock
======================================

First, we'll need a ``rockcraft.yaml`` file. Rockcraft will automate its
creation and tailoring for a Flask application by using the
``flask-framework`` profile:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

The ``rockcraft.yaml`` file will automatically be created in your working
directory. Open it in a text editor and check that the ``name`` is
``flask-hello-world``. Ensure that ``platforms`` includes the architecture of
your host. For example, if your host uses the ARM
architecture, include ``arm64`` in ``platforms``.

.. note::
    For this tutorial, we'll use the ``name`` ``flask-hello-world`` and assume
    you are running on an ``amd64`` platform. Check the architecture of your
    system using ``dpkg --print-architecture``.

    The ``name``, ``version`` and ``platform`` all influence the name of the
    generated ``.rock`` file.

Pack the rock:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

.. note::

    Depending on your network, this step can take a couple of minutes to finish.

Once Rockcraft has finished packing the Flask rock, you'll find a new file in
your working directory (an `OCI <OCI_image_spec_>`_ archive) with the ``.rock``
extension:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2

The created rock is about 65MB in size. We will reduce its size later in this
tutorial.

.. note::
    If you changed the ``name`` or ``version`` in ``rockcraft.yaml`` or are not
    on an ``amd64`` platform, the name of the ``.rock`` file will be different
    for you.

    The size of your rock may vary depending on factors like the architecture
    you are building on and the packages installed at the time of packing.

Run the Flask rock with Docker
==============================

We already have the rock as an `OCI <OCI_image_spec_>`_ archive. Now we
need to load it into Docker:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Check that the image was successfully loaded into Docker:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:docker-images]
    :end-before: [docs:docker-images-end]
    :dedent: 2

The output should list the Flask container image, along with its tag, ID and
size:

..  code-block:: text
    :class: log-snippets

    REPOSITORY          TAG       IMAGE ID       CREATED       SIZE
    flask-hello-world   0.1       c256056698ba   2 weeks ago   149MB

.. note::
    The size of the image reported by Docker is the uncompressed size which is
    larger than the size of the compressed ``.rock`` file.

Now we're finally ready to run the rock and test your containerised Flask
application:

.. literalinclude:: code/flask/task.yaml
    :language: text
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use the same ``curl`` command as before to send a request to the Flask
application's root endpoint which is running inside the container:

.. literalinclude:: code/flask/task.yaml
    :language: text
    :start-after: [docs:curl-flask-rock]
    :end-before: [docs:curl-flask-rock-end]
    :dedent: 2

The Flask application should again respond with ``Hello, world!``.

View the application logs
~~~~~~~~~~~~~~~~~~~~~~~~~

When deploying the Flask rock, you can always get the application logs via
``pebble``:

.. literalinclude:: code/flask/task.yaml
    :language: text
    :start-after: [docs:get-logs]
    :end-before: [docs:get-logs-end]
    :dedent: 2

As a result, :ref:`pebble_explanation_page` will give you the logs for the
``flask`` service running inside the container.
You should expect to see something similar to this:

..  code-block:: text
    :class: log-snippets

    2024-06-21T03:41:45.077Z [flask] [2024-06-21 03:41:45 +0000] [17] [INFO] Starting gunicorn 22.0.0
    2024-06-21T03:41:45.077Z [flask] [2024-06-21 03:41:45 +0000] [17] [INFO] Listening at: http://0.0.0.0:8000 (17)
    2024-06-21T03:41:45.077Z [flask] [2024-06-21 03:41:45 +0000] [17] [INFO] Using worker: sync
    2024-06-21T03:41:45.078Z [flask] [2024-06-21 03:41:45 +0000] [18] [INFO] Booting worker with pid: 18

You can also choose to follow the logs by using the ``-f`` option with the
``pebble logs`` command above. To stop following the logs, press ``ctrl + c``.

Cleanup
~~~~~~~

Now we have a fully functional rock for a Flask application! This concludes
the first part of this tutorial, so we'll stop the container and remove the
respective image for now:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2

Chisel the rock
===============

This is an optional but recommended step, especially if you're looking to
deploy your rock into a production environment. With :ref:`chisel_explanation`
you can produce lean and production-ready rocks by getting rid of all the
contents that are not needed for your Flask application to run. This results
in a much smaller rock with a reduced attack surface.

.. note::
    It is recommended to run chiselled images in production. For development,
    you may prefer non-chiselled images as they will include additional
    development tooling (such as for debugging).

The first step towards chiselling the rock is to ensure we are using a
``bare`` :ref:`base <bases_explanation>`.
In ``rockcraft.yaml``, change the ``base`` to ``bare`` and add
``build-base: ubuntu@22.04``:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:change-base]
    :end-before: [docs:change-base-end]
    :dedent: 2

.. note::
    The ``sed`` command replaces the current ``base`` in ``rockcraft.yaml`` with
    the ``bare`` base. The command also adds a ``build-base`` which is required
    when using the ``bare`` base.

So that we can compare the size after chiselling, **open the**
``rockcraft.yaml`` file and change the ``version`` (e.g. to ``0.1-chiselled``).
Pack the rock with the new ``bare`` :ref:`base <bases_explanation>`:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:chisel-pack]
    :end-before: [docs:chisel-pack-end]
    :dedent: 2

As before, verify that the new rock was created:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:ls-bare-rock]
    :end-before: [docs:ls-bare-rock-end]
    :dedent: 2

You'll verify that the new Flask rock is now approximately **30% smaller**
in size! And that's just because of the simple change of ``base``.

And the functionality is still the same. As before, we can confirm this by
running the rock with Docker

.. literalinclude:: code/flask/task.yaml
    :language: text
    :start-after: [docs:docker-run-chisel]
    :end-before: [docs:docker-run-chisel-end]
    :dedent: 2

and then using the same ``curl`` request:

.. literalinclude:: code/flask/task.yaml
    :language: text
    :start-after: [docs:curl-flask-bare-rock]
    :end-before: [docs:curl-flask-bare-rock-end]
    :dedent: 2

Unsurprisingly, the Flask application should still respond with
``Hello, world!``.

Cleanup
~~~~~~~

And that's it. We can now stop the container and remove the corresponding
image:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-chisel]
    :end-before: [docs:stop-docker-chisel-end]
    :dedent: 2

.. _update-flask-application:

Update Flask application
========================

As a final step, let's update our application. For example,
we want to add a new ``/time`` endpoint which returns the current time.

Start by opening the ``app.py`` file in a text editor and update the code to
look like the following:

.. literalinclude:: code/flask/time_app.py
    :language: python

Since we are creating a new version of the application, **open the**
``rockcraft.yaml`` file and change the ``version`` (e.g. to ``0.2``).

.. note::

    ``rockcraft pack`` will create a new image with the updated code even if you
    don't change the version. It is recommended to change the version whenever
    you make changes to the application in the image.

Pack and run the rock using similar commands as before:

.. literalinclude:: code/flask/task.yaml
    :language: text
    :start-after: [docs:docker-run-update]
    :end-before: [docs:docker-run-update-end]
    :dedent: 2

.. note::

    Note that the resulting ``.rock`` file will now be named differently, as
    its new version will be part of the filename.

Finally, use ``curl`` to send a request to the ``/time`` endpoint:

.. literalinclude:: code/flask/task.yaml
    :language: text
    :start-after: [docs:curl-time]
    :end-before: [docs:curl-time-end]
    :dedent: 2

The updated application should respond with the current date and time (e.g.
``2024-06-21 09:47:56``).

.. note::

    If you are getting a ``404`` for the ``/time`` endpoint, check the
    :ref:`troubleshooting-flask` steps below.

Cleanup
~~~~~~~

We can now stop the container and remove the corresponding image:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-updated]
    :end-before: [docs:stop-docker-updated-end]
    :dedent: 2

Reset your environment
======================

We've reached the end of this tutorial.

If you'd like to reset your working environment, you can simply run the
following:

.. literalinclude:: code/flask/task.yaml
    :language: bash
    :start-after: [docs:cleanup]
    :end-before: [docs:cleanup-end]
    :dedent: 2

.. collapse:: If using Multipass...

    If you created an instance using Multipass, you can also clean it up.
    Start by exiting it:

    .. code-block:: bash

        exit

    And then you can proceed with its deletion:

    .. code-block:: bash

        multipass delete rock-dev
        multipass purge

----

.. _troubleshooting-flask:

Troubleshooting
===============

**Application updates not taking effect?**

Upon changing your Flask application and re-packing the rock, if you believe
your changes are not taking effect (e.g. the ``/time``
:ref:`endpoint <update-flask-application>` is returning a
404), try running ``rockcraft clean`` and pack the rock again with
``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/how-to-install-multipass
