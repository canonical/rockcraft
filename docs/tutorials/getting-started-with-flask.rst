.. _build-a-rock-for-a-flask-application:

Build a rock for a Flask application
------------------------------------

In this tutorial you will create a simple Flask application and learn how to
containerise it in a rock, using Rockcraft's ``flask-framework``
:ref:`extension <flask-framework-reference>`.

Setup
=====

.. include:: /reuse/tutorials/setup.rst

Finally, create a new directory for this tutorial and go inside it:

.. code-block:: bash

   mkdir flask-hello-world
   cd flask-hello-world

Note that you'll also need a text editor. You can either install one of your
choice or simply use one of the already existing editors in your Ubuntu
environment (like ``vi``).

Create the Flask application
============================

Start by creating the "Hello, world" Flask application that will be used for
this tutorial.

Create a ``requirements.txt`` file, copy the following text into it and then
save it:

.. literalinclude:: code/getting-started-with-flask/requirements.txt

In order to test the Flask application locally (before packing it into a rock),
install ``python3-venv`` and create a virtual environment:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:create-venv]
    :end-before: [docs:create-venv-end]
    :dedent: 2

In the same directory, copy and save the following into a text file called
``app.py``:

.. literalinclude:: code/getting-started-with-flask/app.py
    :language: python

Run the Flask application to verify that it works:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:run-flask]
    :end-before: [docs:run-flask-end]
    :dedent: 2

.. note::
    The ``&`` at the end of the command runs the Flask application in the
    background. You can continue to use your terminal as normal and will see all
    the output from the Flask application in your terminal. To stop the Flask
    application, you can use the ``kill`` command shown below.

Test the Flask application by using ``curl`` to send a request to the root
endpoint:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:curl-flask]
    :end-before: [docs:curl-flask-end]
    :dedent: 2

The Flask application should respond with ``Hello, world!``.

The Flask application looks good, so you can stop for now:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:stop-flask]
    :end-before: [docs:stop-flask-end]
    :dedent: 2

Pack the Flask application into a rock
======================================

First, you'll need a ``rockcraft.yaml`` file. Rockcraft will automate its
creation and tailoring for a Flask application by using the
``flask-framework`` profile:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

The ``rockcraft.yaml`` file will automatically be created in your working
directory. Open it in a text editor and customise the ``name``,
``summary`` and ``description``. Ensure that ``platforms`` includes
the architecture of your host. For example, if your host uses the ARM
architecture, include ``arm64`` in ``platforms``.

.. note::
    For this tutorial, we'll use the ``name`` "flask-hello-world" and build
    the rock on an ``amd64`` platform.

Pack the rock:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

.. note::

    Depending on your network, this step can take a couple of minutes to finish.

Once Rockcraft has finished packing the Flask rock, you'll find a new file in
your working directory (an `OCI <OCI_image_spec_>`_ archive) with the ``.rock``
extension:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2

The created rock is about 62MB in size. We will reduce its size later in this
tutorial.

.. note::
    If you changed the ``name`` or ``version`` in ``rockcraft.yaml`` or are not
    on an ``amd64`` platform, the name of the ``.rock`` file will be different
    for you.

Run the Flask rock with Docker
==============================

You already have the rock as an `OCI <OCI_image_spec_>`_ archive. Now you'll
need to import it into a format that Docker recognises:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Check that the image was successfully imported into Docker:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:docker-images]
    :end-before: [docs:docker-images-end]
    :dedent: 2

The output should list your Flask container image, along with its tag, ID and
size:

..  code-block:: text
    :class: log-snippets

    REPOSITORY          TAG       IMAGE ID       CREATED       SIZE
    flask-hello-world   0.1       c256056698ba   2 weeks ago   149MB

.. note::
    The size of the image reported by Docker is the uncompressed size which is
    larger than the size of the compressed ``.rock`` file.

Now you're finally ready to run the rock and test your containerised Flask
application:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: text
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use the same ``curl`` command as before to send a request to the Flask
application's root endpoint which is running inside the container:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: text
    :start-after: [docs:curl-flask-rock]
    :end-before: [docs:curl-flask-rock-end]
    :dedent: 2

The Flask application should again respond with ``Hello, world!``.

View the application logs
~~~~~~~~~~~~~~~~~~~~~~~~~

When deploying your Flask rock, you can always get the application logs via
``pebble``:

.. literalinclude:: code/getting-started-with-flask/task.yaml
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
``pebble logs`` command above.

.. important::

    To get the Flask application logs, the container must be running. This is
    also valid for the remaining sections of this tutorial.

Cleanup
~~~~~~~

Now you have a fully functional rock for you Flask application! This concludes
the first part of this tutorial, so you can stop the container and remove the
respective image for now:

.. literalinclude:: code/getting-started-with-flask/task.yaml
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

The first step towards chiselling your rock is to ensure you are using a
``bare`` :ref:`base <bases_explanation>`.
In ``rockcraft.yaml``, change the ``base`` to ``bare`` and add
``build-base: ubuntu@22.04``:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:change-base]
    :end-before: [docs:change-base-end]
    :dedent: 2

Pack the rock with the new ``bare`` :ref:`base <bases_explanation>`:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:chisel-pack]
    :end-before: [docs:chisel-pack-end]
    :dedent: 2

As before, verify that the new rock was created:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:ls-bare-rock]
    :end-before: [docs:ls-bare-rock-end]
    :dedent: 2

You'll verify that the new Flask rock is now approximately **15% smaller**
in size! And that's just because of the simple change of ``base``.

And the functionality is still the same. As before, you can confirm this by
running the rock with Docker

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: text
    :start-after: [docs:docker-run-chisel]
    :end-before: [docs:docker-run-chisel-end]
    :dedent: 2

and then using the same ``curl`` request:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: text
    :start-after: [docs:curl-flask-bare-rock]
    :end-before: [docs:curl-flask-bare-rock-end]
    :dedent: 2

Unsurprisingly, the Flask application should still respond with
``Hello, world!``.

Cleanup
~~~~~~~

And that's it. You can now stop container and remove the corresponding image:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-chisel]
    :end-before: [docs:stop-docker-chisel-end]
    :dedent: 2

.. _update-flask-application:

Update Flask application
========================

As a final step, let's say you want to update your application. For example,
you want to add a new ``/time`` endpoint which returns the current time.

Start by opening the ``app.py`` file in a text editor and update the code to
look like the following:

.. literalinclude:: code/getting-started-with-flask/time-app.py
    :language: python

Since you are creating a new version of your application, **open the**
``rockfile.yaml`` **file and change the** ``version`` (e.g. to ``0.2``).

Pack and run the rock using similar commands as before:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: text
    :start-after: [docs:docker-run-update]
    :end-before: [docs:docker-run-update-end]
    :dedent: 2

.. note::

    Note that the resulting ``.rock`` file will now be named differently, as
    its new version will be part of the filename.

Finally, use ``curl`` to send a request to the ``/time`` endpoint:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: text
    :start-after: [docs:curl-time]
    :end-before: [docs:curl-time-end]
    :dedent: 2

The updated application should respond with the current date and time (e.g.
``2024-06-21 09:47:56``).

Cleanup
~~~~~~~

You can now stop container and remove the corresponding image:

.. literalinclude:: code/getting-started-with-flask/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-updated]
    :end-before: [docs:stop-docker-updated-end]
    :dedent: 2

Reset your environment
======================

You've reached the end of this tutorial.

If you'd like to reset your working environment, you can simply run the
following:

.. literalinclude:: code/getting-started-with-flask/task.yaml
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
