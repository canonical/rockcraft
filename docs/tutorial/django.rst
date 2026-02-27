.. _tutorial-build-a-rock-for-a-django-app:

Build a rock for a Django app
-----------------------------

In this tutorial, we'll create a simple Django app and learn how to
containerise it in a rock, using Rockcraft's ``django-framework``
:ref:`extension <reference-django-framework>`.

Setup
=====

.. include:: /reuse/tutorial/setup_stable.rst

Finally, create an empty project directory:

.. code-block:: bash

   mkdir django-hello-world
   cd django-hello-world

Create the Django app
=====================

Start by creating the "Hello, world" Django app that will be used for
this tutorial.

Create a ``requirements.txt`` file, copy the following text into it and then
save it:

.. literalinclude:: code/django/requirements.txt
    :caption: ~/django-hello-world/requirements.txt

In order to test the Django app locally (before packing it into a rock),
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

Change into the ``django_hello_world`` directory and run the Django app
using ``python manage.py runserver`` to verify that it works.

Test the Django app by using ``curl`` to send a request to the root
endpoint. We'll need a new shell of the VM for this -- in a separate terminal,
run ``multipass shell rock-dev`` again:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:curl-django]
    :end-before: [docs:curl-django-end]
    :dedent: 2

The Django app should respond with
``The install worked successfully! Congratulations!``.

.. note::
    The response from the Django app includes HTML and CSS which makes
    it difficult to read on a terminal. To see the fully-rendered page
    in a web browser, set ``ALLOWED_HOSTS = ['*']`` in
    ``~/django-hello-world/django_hello_world/settings.py`` and run the Django app
    using:

    .. code-block:: bash

        python manage.py runserver 0.0.0.0:8000

    Determine the IP address of your VM. Outside of the VM, run:

    .. code-block:: bash

        multipass info rock-dev | grep IP

    Visit ``http://<Multipass private IP>:8000``
    in a web browser to see the fully-rendered page, replacing
    ``<Multipass private IP>`` with your VM's private IP address.

The Django app looks good, so let's close the terminal instance we used for
testing and stop the app in the original terminal instance by pressing
:kbd:`Ctrl` + :kbd:`C`.

Pack the Django app into a rock
===============================

Now let's create a container image for our Django app. We'll use a rock,
which is an OCI-compliant container image based on Ubuntu.

First, we'll need a ``rockcraft.yaml`` project file. We'll take advantage of a
pre-defined extension in Rockcraft with the ``--profile`` flag that caters
initial rock files for specific web app frameworks. Using the
Django profile, Rockcraft automates the creation of
``rockcraft.yaml`` and tailors the file for a Django app. Change
back into the ``~/django-hello-world`` directory and initialize the rock:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

The project file will automatically be created in the working directory as
``rockcraft.yaml``.

Check out the contents of ``rockcraft.yaml``:

.. code-block:: bash

    cat rockcraft.yaml

The top of the file should look similar to the following snippet:

.. code-block:: yaml
    :caption: ~/django-hello-world/rockcraft.yaml

    name: django-hello-world
    # see https://documentation.ubuntu.com/rockcraft/en/1.6.0/explanation/bases/
    # for more information about bases and using 'bare' bases for chiselled rocks
    base: bare # as an alternative, an ubuntu base can be used
    build-base: ubuntu@24.04 # build-base is required when the base is bare
    version: '0.1' # just for humans. Semantic versioning is recommended
    summary: A summary of your Django app # 79 char long summary
    description: |
        This is django-hello-world's description. You have a paragraph or two to tell the
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

Verify that the ``name`` is ``django-hello-world``.

The ``platforms`` key must match the architecture of your host. Check
the architecture of your system:

.. code-block:: bash

    dpkg --print-architecture

Edit the ``platforms`` key in ``rockcraft.yaml`` if required.

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

.. include:: /reuse/troubleshooting/lxd-docker-networking.rst

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

Run the Django rock with Docker
===============================

We already have the rock as an `OCI <OCI_image_spec_>`_ archive. Now we'll
need to load it into Docker. Docker requires rocks to be imported into the
daemon since they can't be run directly like an executable.

Copy the rock:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

This command contains the following pieces:

- ``--insecure-policy``: adopts a permissive policy that
  removes the need for a dedicated policy file.
- ``oci-archive``: specifies the rock we created for our Django app.
- ``docker-daemon``: specifies the name of the image in the Docker registry.

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

Now we're ready to run the rock and test the containerised Django app:

.. literalinclude:: code/django/task.yaml
    :language: text
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use the same ``curl`` command as before to send a request to the Django
app's root endpoint which is running inside the container:

.. literalinclude:: code/django/task.yaml
    :language: text
    :start-after: [docs:curl-django-rock]
    :end-before: [docs:curl-django-rock-end]
    :dedent: 2

The Django app should again respond with
``The install worked successfully! Congratulations!``.

View the app logs
~~~~~~~~~~~~~~~~~

When deploying the Django rock, we can always get the app logs via
:ref:`explanation-pebble`:

.. literalinclude:: code/django/task.yaml
    :language: text
    :start-after: [docs:get-logs]
    :end-before: [docs:get-logs-end]
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

Now we have a fully functional rock for our Django app! This concludes
the first part of this tutorial, so we can stop the container and remove the
respective image for now:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2

Chisel the rock
===============

This is an optional but recommended step, especially if we're looking to
deploy the rock into a production environment. With :ref:`explanation-chisel`
we can produce lean and production-ready rocks by getting rid of all the
contents that are not needed for the Django app to run. This results
in a much smaller rock with a reduced attack surface.

.. note::
    It is recommended to run chiselled images in production. For development,
    we may prefer non-chiselled images as they will include additional
    development tooling (such as for debugging).

The first step towards chiselling the rock is to ensure we are using a
``bare`` :ref:`base <explanation-bases>`.

So that we can compare the size after chiselling, open the project
file and change the ``version`` (e.g. to ``0.1-chiselled``). The top of
the ``rockcraft.yaml`` file should look similar to the following:

.. code-block:: yaml
    :caption: ~/django-hello-world/rockcraft.yaml
    :emphasize-lines: 6

    name: django-hello-world
    # see https://documentation.ubuntu.com/rockcraft/en/1.6.0/explanation/bases/
    # for more information about bases and using 'bare' bases for chiselled rocks
    base: bare
    build-base: ubuntu@24.04
    version: '0.1-chiselled'
    summary: A summary of your Django app # 79 char long summary
    description: |
        This is django-hello-world's description. You have a paragraph or two to tell the
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

Pack the rock with the new ``bare`` base:

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
running the rock with Docker:

.. literalinclude:: code/django/task.yaml
    :language: text
    :start-after: [docs:docker-run-chisel]
    :end-before: [docs:docker-run-chisel-end]
    :dedent: 2

and then using the same ``curl`` request:

.. literalinclude:: code/django/task.yaml
    :language: text
    :start-after: [docs:curl-django-bare-rock]
    :end-before: [docs:curl-django-bare-rock-end]
    :dedent: 2

The Django app should still respond with
``The install worked successfully! Congratulations!``.

Cleanup
~~~~~~~

And that's it. We can now stop the container and remove the corresponding
image:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-chisel]
    :end-before: [docs:stop-docker-chisel-end]
    :dedent: 2

.. _update-django-application:

Update the Django app
=====================

As a final step, let's update our app. For example,
we want to add a new ``/time/`` endpoint which returns the current time.

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:create-time-app]
    :end-before: [docs:create-time-app-end]
    :dedent: 2

Open the file ``time_app/views.py`` and replace its contents with the following:

.. literalinclude:: code/django/time_app_views.py
    :caption: ~/django-hello-world/django_hello_world/time_app/views.py
    :language: python

Create the file ``time_app/urls.py`` with the following contents:

.. literalinclude:: code/django/time_app_urls.py
    :caption: ~/django-hello-world/django_hello_world/time_app/urls.py
    :language: python

Open the file ``django_hello_world/urls.py`` and replace its contents with
the following:

.. literalinclude:: code/django/urls.py
    :caption: ~/django-hello-world/django_hello_world/django_hello_world/urls.py
    :language: python

Since we are creating a new version of the app, go back to the
tutorial root directory using ``cd ..`` and open the project file and
change the ``version`` (e.g. to ``0.2``). The top of
the ``rockcraft.yaml`` file should look similar to the following:

.. code-block:: yaml
    :caption: ~/django-hello-world/rockcraft.yaml
    :emphasize-lines: 6

    name: django-hello-world
    # see https://documentation.ubuntu.com/rockcraft/en/1.6.0/explanation/bases/
    # for more information about bases and using 'bare' bases for chiselled rocks
    base: bare
    build-base: ubuntu@24.04
    version: '0.2'
    summary: A summary of your Django app # 79 char long summary
    description: |
        This is django-hello-world's description. You have a paragraph or two to tell the
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

.. literalinclude:: code/django/task.yaml
    :language: text
    :start-after: [docs:docker-run-update]
    :end-before: [docs:docker-run-update-end]
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

The updated app should respond with the current date and time (e.g.
``2024-08-20 07:28:19``).

.. note::

    If you are getting a ``404`` for the ``/time/`` endpoint, check the
    :ref:`troubleshooting-django` steps below.

Cleanup
~~~~~~~

We can now stop the container and remove the corresponding image:

.. literalinclude:: code/django/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-updated]
    :end-before: [docs:stop-docker-updated-end]
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

We can also clean the Multipass instance up.
Start by exiting it:

.. code-block:: bash

    exit

And then we can proceed with its deletion:

.. code-block:: bash

    multipass delete rock-dev
    multipass purge

Next steps
==========

Congratulations! You've reached the end of this tutorial. You created a
Django app, packaged it into a rock, and practiced some typical development skills
such as viewing logs and updating the app.

But there is a lot more to explore:

.. list-table::
    :widths: 30 30
    :header-rows: 1

    * - If you are wondering...
      - Visit...
    * - "What's next?"
      - :external+charmcraft:ref:`Write your first Kubernetes charm for a Django app
        in Charmcraft <write-your-first-kubernetes-charm-for-a-django-app>`
    * - "How do I...?"
      - :ref:`how-to-manage-a-12-factor-app-rock`
    * - "How do I get in touch?"
      - `Matrix channel <https://matrix.to/#/#12-factor-charms:ubuntu.com>`_
    * - "What is...?"
      - :ref:`django-framework extension <reference-django-framework>`

        :ref:`What is a Rock? <explanation-rocks>`
    * - "Why...?", "So what?"
      - :external+12-factor:ref:`12-Factor app principles and support in Charmcraft
        and Rockcraft <explanation>`

----

.. _troubleshooting-django:

Troubleshooting
===============

**App updates not taking effect?**

Upon changing your Django app and re-packing the rock, if you believe
your changes are not taking effect (e.g. the ``/time/``
:ref:`endpoint <update-django-application>` is returning a
404), try running ``rockcraft clean`` and pack the rock again with
``rockcraft pack``.

