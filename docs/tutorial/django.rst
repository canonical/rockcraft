.. _build-a-rock-for-a-django-application:

Build a rock for a Django application
-------------------------------------

In this tutorial, we'll create a simple Django application and learn how to
containerise it in a rock, using Rockcraft's ``django-framework``
:ref:`extension <django-framework-reference>`.

Setup
=====

.. include:: /reuse/tutorial/setup_stable.rst

Finally, create a new directory for this tutorial and go inside it:

.. code-block:: bash

   mkdir django-hello-world
   cd django-hello-world

Create the Django application
=============================

Start by creating the "Hello, world" Django application that will be used for
this tutorial.

Create a ``requirements.txt`` file, copy the following text into it and then
save it:

.. literalinclude:: code/django/requirements.txt

In order to test the Django application locally (before packing it into a rock),
install ``python3-venv`` and create a virtual environment:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:create-venv]
    :end-before: [docs:create-venv-end]
    :dedent: 2

Create a new project using ``django-admin``:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:create-project]
    :end-before: [docs:create-project-end]
    :dedent: 2

Change into the ``django_hello_world`` directory and run the Django application
using ``python manage.py runserver`` to verify that it works.

Test the Django application by using ``curl`` to send a request to the root
endpoint. We'll need a new terminal for this -- if we're using Multipass, run
``multipass shell rock-dev`` to get another terminal:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:curl-django]
    :end-before: [docs:curl-django-end]
    :dedent: 2

The Django application should respond with
``The install worked successfully! Congratulations!``.

.. note::
    The response from the Django application includes HTML and CSS which makes
    it difficult to read on a terminal. Visit ``http://localhost:8000`` using a
    browser to see the fully rendered page.

The Django application looks good, so let's stop it for now by pressing
:kbd:`Ctrl` + :kbd:`C`.

Pack the Django application into a rock
=======================================

First, we'll need a project file. Rockcraft will automate its
creation and tailoring for a Django application by using the
``django-framework`` profile:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

The project file will automatically be created in the working directory as
``rockcraft.yaml``. Open it in a text editor and check that the ``name`` is
``django-hello-world``. Ensure that ``platforms`` includes the host
architecture. For example, if the host uses the ARM architecture, include
``arm64`` in ``platforms``.

.. note::
    For this tutorial, we'll use the ``name`` ``django-hello-world`` and assume
    we're running on the ``amd64`` platform. Check the architecture of the
    system using ``dpkg --print-architecture``.

    The ``name``, ``version`` and ``platform`` all influence the name of the
    generated ``.rock`` file.

Pack the rock:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

.. note::

    Depending on the network, this step can take a couple of minutes to finish.

Once Rockcraft has finished packing the Django rock, we'll find a new file in
the project's working directory (an `OCI <OCI_image_spec_>`_ archive) with
the ``.rock`` extension:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2

The created rock is about 75MB in size. We will reduce its size later in this
tutorial.

.. note::
    If we changed the ``name`` or ``version`` in the project file or are not
    on an ``amd64`` platform, the name of the ``.rock`` file will be
    different.

    The size of the rock may vary depending on factors like the architecture
    we are building on and the packages installed at the time of packing.

Run the Django rock
====================

We already have the rock as an `OCI <OCI_image_spec_>`_ archive. Now we'll
need to run it:

.. tabs::

    .. group-tab:: Docker

        We first load it into Docker:

        .. literalinclude:: code/django/task.yaml
            :language: bash
            :start-after: [docs:skopeo-copy]
            :end-before: [docs:skopeo-copy-end]
            :dedent: 2

        Check that the image was successfully loaded into Docker:

        .. literalinclude:: code/django/task.yaml
            :language: bash
            :start-after: [docs:docker-images]
            :end-before: [docs:docker-images-end]
            :dedent: 2

        The output should list the Django container image, along with its tag, ID and
        size:

        .. terminal::

            REPOSITORY          TAG       IMAGE ID       CREATED       SIZE
            django-hello-world  0.1       5cd019b51db9   6 days ago   184MB

        .. note::
            The size of the image reported by Docker is the uncompressed size which is
            larger than the size of the compressed ``.rock`` file.

        Now we're ready to run the rock and test the containerised Django application:

        .. literalinclude:: code/django/task.yaml
            :language: text
            :start-after: [docs:docker-run]
            :end-before: [docs:docker-run-end]
            :dedent: 2

    .. group-tab:: Podman

        We can run directly from the OCI Archive using Podman:

        .. literalinclude:: code/django/task.yaml
            :language: text
            :start-after: [docs:podman-run]
            :end-before: [docs:podman-run-end]
            :dedent: 2

Use the same ``curl`` command as before to send a request to the Django
application's root endpoint which is running inside the container:

.. literalinclude:: code/django/task.yaml
    :language: text
    :start-after: [docs:curl-django-rock]
    :end-before: [docs:curl-django-rock-end]
    :dedent: 2

The Django application should again respond with
``The install worked successfully! Congratulations!``.

View the application logs
~~~~~~~~~~~~~~~~~~~~~~~~~

When deploying the Django rock, we can always get the application logs via
:ref:`pebble_explanation_page`:

.. tabs::

    .. group-tab:: Docker

        With Docker:

        .. literalinclude:: code/django/task.yaml
            :language: text
            :start-after: [docs:get-logs]
            :end-before: [docs:get-logs-end]
            :dedent: 2

    .. group-tab:: Podman

        With Podman:

        .. literalinclude:: code/django/task.yaml
            :language: text
            :start-after: [docs:get-logs-podman]
            :end-before: [docs:get-logs-podman-end]
            :dedent: 2

As a result, Pebble will give us the logs for the
``django`` service running inside the container.
We should expect to see something similar to this:

.. terminal::

    2024-08-20T06:34:36.114Z [django] [2024-08-20 06:34:36 +0000] [17] [INFO] Starting gunicorn 23.0.0
    2024-08-20T06:34:36.115Z [django] [2024-08-20 06:34:36 +0000] [17] [INFO] Listening at: http://0.0.0.0:8000 (17)
    2024-08-20T06:34:36.115Z [django] [2024-08-20 06:34:36 +0000] [17] [INFO] Using worker: sync
    2024-08-20T06:34:36.116Z [django] [2024-08-20 06:34:36 +0000] [18] [INFO] Booting worker with pid: 18

We can also choose to follow the logs by using the ``-f`` option with the
``pebble logs`` command above. To stop following the logs, press :kbd:`Ctrl` +
:kbd:`C`.

Cleanup
~~~~~~~

Now we have a fully functional rock for our Django application! This concludes
the first part of this tutorial, so we can stop the container and remove the
respective image for now:

.. tabs::

    .. group-tab:: Docker

        .. literalinclude:: code/django/task.yaml
            :language: bash
            :start-after: [docs:stop-docker]
            :end-before: [docs:stop-docker-end]
            :dedent: 2

    .. group-tab:: Podman

        .. literalinclude:: code/django/task.yaml
            :language: bash
            :start-after: [docs:stop-podman]
            :end-before: [docs:stop-podman-end]
            :dedent: 2

Chisel the rock
===============

This is an optional but recommended step, especially if we're looking to
deploy the rock into a production environment. With :ref:`chisel_explanation`
we can produce lean and production-ready rocks by getting rid of all the
contents that are not needed for the Django application to run. This results
in a much smaller rock with a reduced attack surface.

.. note::
    It is recommended to run chiselled images in production. For development,
    we may prefer non-chiselled images as they will include additional
    development tooling (such as for debugging).

The first step towards chiselling the rock is to ensure we are using a
``bare`` :ref:`base <bases_explanation>`.
In the project file, change the ``base`` to ``bare`` and add
``build-base: ubuntu@22.04``:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:change-base]
    :end-before: [docs:change-base-end]
    :dedent: 2

So that we can compare the size after chiselling, open the project
file and change the ``version`` (e.g. to ``0.1-chiselled``). Pack the rock with
the new ``bare`` :ref:`base <bases_explanation>`:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:chisel-pack]
    :end-before: [docs:chisel-pack-end]
    :dedent: 2

As before, verify that the new rock was created:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:ls-bare-rock]
    :end-before: [docs:ls-bare-rock-end]
    :dedent: 2

We'll verify that the new Django rock is now approximately **15% smaller**
in size! And that's just because of the simple change of ``base``.

And the functionality is still the same. As before, we can confirm this by
running the rock with:

.. tabs::

    .. group-tab:: Docker

        With Docker:

        .. literalinclude:: code/django/task.yaml
            :language: text
            :start-after: [docs:docker-run-chisel]
            :end-before: [docs:docker-run-chisel-end]
            :dedent: 2

    .. group-tab:: Podman

        With Podman:

        .. literalinclude:: code/django/task.yaml
            :language: text
            :start-after: [docs:podman-run-chisel]
            :end-before: [docs:podman-run-chisel-end]
            :dedent: 2

and then using the same ``curl`` request:

.. literalinclude:: code/django/task.yaml
    :language: text
    :start-after: [docs:curl-django-bare-rock]
    :end-before: [docs:curl-django-bare-rock-end]
    :dedent: 2

The Django application should still respond with
``The install worked successfully! Congratulations!``.

Cleanup
~~~~~~~

And that's it. We can now stop the container and remove the corresponding
image:

.. tabs::

    .. group-tab:: Docker

        .. literalinclude:: code/django/task.yaml
            :language: bash
            :start-after: [docs:stop-docker-chisel]
            :end-before: [docs:stop-docker-chisel-end]
            :dedent: 2

    .. group-tab:: Podman

        .. literalinclude:: code/django/task.yaml
            :language: bash
            :start-after: [docs:stop-podman-chisel]
            :end-before: [docs:stop-podman-chisel-end]
            :dedent: 2


.. _update-django-application:

Update the Django application
=============================

As a final step, let's update our application. For example,
we want to add a new ``/time/`` endpoint which returns the current time.

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:create-time-app]
    :end-before: [docs:create-time-app-end]
    :dedent: 2

Open the file ``time_app/views.py`` and replace its contents with the following:

.. literalinclude:: code/django/time_app_views.py
    :language: python

Create the file ``time_app/urls.py`` with the following contents:

.. literalinclude:: code/django/time_app_urls.py
    :language: python

Open the file ``django_hello_world/urls.py`` and replace its contents with
the following:

.. literalinclude:: code/django/urls.py
    :language: python

Since we are creating a new version of the application, go back to the
tutorial root directory using ``cd ..`` and open the project file and
change the ``version`` (e.g. to ``0.2``).

.. note::

    ``rockcraft pack`` will create a new image with the updated code even if we
    don't change the version. It is recommended to change the version whenever
    we make changes to the application in the image.

Pack and run the rock using similar commands as before:

.. tabs::

    .. group-tab:: Docker

        .. literalinclude:: code/django/task.yaml
            :language: text
            :start-after: [docs:docker-run-update]
            :end-before: [docs:docker-run-update-end]
            :dedent: 2

    .. group-tab:: Podman

        .. literalinclude:: code/django/task.yaml
            :language: text
            :start-after: [docs:podman-run-update]
            :end-before: [docs:podman-run-update-end]
            :dedent: 2

.. note::

    Note that the resulting ``.rock`` file will now be named differently, as
    its new version will be part of the filename.

Finally, use ``curl`` to send a request to the ``/time/`` endpoint:

.. literalinclude:: code/django/task.yaml
    :language: text
    :start-after: [docs:curl-time]
    :end-before: [docs:curl-time-end]
    :dedent: 2

The updated application should respond with the current date and time (e.g.
``2024-08-20 07:28:19``).

.. note::

    If you are getting a ``404`` for the ``/time/`` endpoint, check the
    :ref:`troubleshooting-django` steps below.

Cleanup
~~~~~~~

We can now stop the container and remove the corresponding image:


.. tabs::

    .. group-tab:: Docker

        .. literalinclude:: code/django/task.yaml
            :language: bash
            :start-after: [docs:stop-docker-updated]
            :end-before: [docs:stop-docker-updated-end]
            :dedent: 2

    .. group-tab:: Podman

        .. literalinclude:: code/django/task.yaml
            :language: bash
            :start-after: [docs:stop-podman-updated]
            :end-before: [docs:stop-podman-updated-end]
            :dedent: 2

Reset the environment
=====================

We've reached the end of this tutorial.

If we'd like to reset the working environment, we can simply run the
following:

.. literalinclude:: code/django/task.yaml
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

.. _troubleshooting-django:

Troubleshooting
===============

**Application updates not taking effect?**

Upon changing your Django application and re-packing the rock, if you believe
your changes are not taking effect (e.g. the ``/time/``
:ref:`endpoint <update-django-application>` is returning a
404), try running ``rockcraft clean`` and pack the rock again with
``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/install-multipass
