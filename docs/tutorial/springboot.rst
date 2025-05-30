.. _build-a-rock-for-a-spring-boot-application:

Build a rock for a Spring Boot application
------------------------------------------

In this tutorial, we'll containerise a simple Spring Boot application into a
rock using Rockcraft's ``spring-boot-framework``
:ref:`extension <spring-boot-framework-reference>`.

It should take 25 minutes for you to complete.

You won’t need to come prepared with intricate knowledge of software
packaging, but familiarity with Linux paradigms, terminal operations,
and Spring Boot is required.

Once you complete this tutorial, you’ll have a working rock for a
Spring Boot application. You’ll gain familiarity with Rockcraft and the
``spring-boot-framework`` extension, and have the experience to create
rocks for Spring Boot applications.

Setup
=====

.. include:: /reuse/tutorial/setup_edge.rst

In order to test the Spring Boot application locally, before packing it into a rock,
install ``devpack-for-spring`` and Java.

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:install-devpack-for-spring]
    :end-before: [docs:install-devpack-for-spring-end]
    :dedent: 2


Create the Spring Boot application
==================================

Start by creating the Demo Spring Boot application that will be used for
this tutorial.

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:init-spring-boot]
    :end-before: [docs:init-spring-boot-end]
    :dedent: 2


Build the Spring Boot application so it can be run:

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:spring-boot-build]
    :end-before: [docs:spring-boot-build-end]
    :dedent: 2

A jar called ``demo-0.0.1.jar`` is created in the ``target``
directory. This jar is only needed for local testing, as
Rockcraft will package the Spring Boot application when we pack the rock.

Let's Run the Spring Boot application to verify that it works:

.. code:: bash

  java -jar target/demo-0.0.1.jar

The application starts an HTTP server listening on port 8000
that we can test by using ``curl`` to send a request to the root
endpoint. We may need a new terminal for this -- if using Multipass, run
``multipass shell rock-dev`` to get another terminal:

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:curl-spring-boot]
    :end-before: [docs:curl-spring-boot-end]
    :dedent: 2

The Spring Boot application should respond with
``{"timestamp":<timestamp>,"status":404,"error":"Not Found","path":"/"}``.

The Spring Boot application looks good, so let's stop it for now
with :kbd:`Ctrl` + :kbd:`C`.

Pack the Spring Boot application into a rock
============================================


First, we'll need a project file. Rockcraft will automate its
creation and tailor it for a Spring Boot application when we tell it to use the
``spring-boot-framework`` profile:

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:create-rockcraft-yaml]
    :end-before: [docs:create-rockcraft-yaml-end]
    :dedent: 2

Open ``rockcraft.yaml`` in a text editor and check that the ``name``
key is set to ``spring-boot-hello-world``. Ensure that ``platforms`` includes
the architecture of the host. For example, if the host uses the ARM
architecture, include ``arm64`` in ``platforms``.

.. note::
    For this tutorial, we name the rock ``spring-boot-hello-world`` and assume
    we are running on an ``amd64`` platform. Check the architecture of the
    system using ``dpkg --print-architecture``.

    The ``name``, ``version`` and ``platform`` all influence the name of the
    generated ``.rock`` file.


As the ``spring-boot-framework`` extension is still experimental, export the
environment variable ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS``:

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:experimental]
    :end-before: [docs:experimental-end]
    :dedent: 2

Pack the rock:

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

Depending on the network, this step can take a couple of minutes to finish.

Once Rockcraft has finished packing the Spring Boot rock, we'll find a new file in
the working directory (an `OCI <OCI_image_spec_>`_ image) with the ``.rock``
extension:

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:ls-rock]
    :end-before: [docs:ls-rock-end]
    :dedent: 2


Run the Spring Boot rock with Docker
====================================


We already have the rock as an `OCI <OCI_image_spec_>`_ archive. Load the
image into Docker:

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

This command contains the following pieces:

- ``--insecure-policy``: adopts a permissive policy that
  removes the need for a dedicated policy file.
- ``oci-archive``: specifies the rock we created for our Spring Boot app.
- ``docker-daemon``: specifies the name of the image in the Docker registry.

Check that the image was successfully loaded into Docker:

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:docker-images]
    :end-before: [docs:docker-images-end]
    :dedent: 2

The output should list the Spring Boot container image, along with its tag, ID and
size:

.. terminal::

    REPOSITORY       TAG       IMAGE ID       CREATED         SIZE
    spring-boot-hello-world   0.1       f3abf7ebc169   5 minutes aspring-boot   15.7MB

Now we're finally ready to run the rock and test the containerised Spring Boot
application:

.. literalinclude:: code/spring-boot/task.yaml
    :language: text
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Use the same ``curl`` command as before to send a request to the Spring Boot
application's root endpoint which is running inside the container:

.. literalinclude:: code/spring-boot/task.yaml
    :language: text
    :start-after: [docs:curl-spring-boot-rock]
    :end-before: [docs:curl-spring-boot-rock-end]
    :dedent: 2

The Spring Boot application again responds with
``{"timestamp":<timestamp>,"status":404,"error":"Not Found","path":"/"}``.


View the application logs
~~~~~~~~~~~~~~~~~~~~~~~~~

When deploying the Spring Boot rock, we can always get the application logs with
:ref:`pebble_explanation_page`:

.. literalinclude:: code/spring-boot/task.yaml
    :language: text
    :start-after: [docs:get-logs]
    :end-before: [docs:get-logs-end]
    :dedent: 2

As a result, Pebble will give the logs for the
``spring-boot`` service running inside the container.
We should expect to see something similar to this:

.. terminal::

     .   ____          _            __ _ _
    /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
    ( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
    \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
    '  |____| .__|_| |_|_| |_\__, | / / / /
    =========|_|==============|___/=/_/_/_/

    :: Spring Boot ::                (v3.4.4)

    2025-04-09T03:48:07.704Z  INFO 4258 --- [demo] [main] com.example.demo.DemoApplication:
    Starting DemoApplication v0.0.1 using Java 21.0.6 with PID <redacted>.

We can also choose to follow the logs by using the ``-f`` option with the
``pebble logs`` command above. To stop following the logs, press :kbd:`Ctrl` + :kbd:`C`.


Stop the application
~~~~~~~~~~~~~~~~~~~~

Now we have a fully functional rock for a Spring Boot application! This concludes
the first part of this tutorial, so we'll stop the container and remove the
respective image for now:

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:stop-docker]
    :end-before: [docs:stop-docker-end]
    :dedent: 2


Update the Spring Boot application
==================================

As a final step, let's update our application. For example,
we want to add a new ``/time`` endpoint which returns the current time.

Start by creating the ``src/main/java/com/example/demo/TimeController.java``
file in a text editor and paste in the code to look like the following:

.. literalinclude:: code/spring-boot/TimeController.java
    :caption: ~/src/main/java/com/example/demo/TimeController.java
    :language: java

Since we are creating a new version of the application, open the project
file and set ``version: '0.2'``.
The top of the ``rockcraft.yaml`` file should look similar to the following:

.. code-block:: yaml
    :caption: ~/rockcraft.yaml
    :emphasize-lines: 6

    name: spring-boot-hello-world
    # see https://documentation.ubuntu.com/rockcraft/en/latest/explanation/bases/
    # for more information about bases and using 'bare' bases for chiselled rocks
    base: bare # as an alternative, a ubuntu base can be used
    build-base: ubuntu@24.04 # build-base is required when the base is bare
    version: '0.2' # just for humans. Semantic versioning is recommended
    summary: A summary of your Go application # 79 char long summary
    description: |
        This is spring-boot-hello-world's description. You have a paragraph or two to tell the
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

    ``rockcraft pack`` will create a new image with the updated code even if we
    don't change the version. It is recommended to change the version whenever
    we make changes to the application in the image.

Pack and run the rock using similar commands as before:

.. literalinclude:: code/spring-boot/task.yaml
    :language: text
    :start-after: [docs:docker-run-update]
    :end-before: [docs:docker-run-update-end]
    :dedent: 2

.. note::

    Note that the resulting ``.rock`` file will now be named differently, as
    its new version will be part of the filename.

Finally, use ``curl`` to send a request to the ``/time`` endpoint:

.. literalinclude:: code/spring-boot/task.yaml
    :language: text
    :start-after: [docs:curl-time]
    :end-before: [docs:curl-time-end]
    :dedent: 2

The updated application will respond with the current date and time.

.. note::

    If we are not getting the current date and time from the ``/time``
    endpoint, check the :ref:`troubleshooting-spring-boot` steps below.


Cleanup
~~~~~~~

We can now stop the container and remove the corresponding image:

.. literalinclude:: code/spring-boot/task.yaml
    :language: bash
    :start-after: [docs:stop-docker-updated]
    :end-before: [docs:stop-docker-updated-end]
    :dedent: 2


Reset the environment
======================

We've reached the end of this tutorial.

If we'd like to reset the working environment, we can simply run the
following:

.. literalinclude:: code/spring-boot/task.yaml
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
* :ref:`spring-boot-framework reference<spring-boot-framework-reference>`.
* :ref:`why_use_rockcraft`.
* :ref:`What is a Rock?<rocks_explanation>`.

----

.. _troubleshooting-spring-boot:

Troubleshooting
===============

**Application updates not taking effect?**

Upon changing the Spring Boot application and re-packing the rock, if
the changes are not taking effect, try running ``rockcraft clean`` and pack
the rock again with ``rockcraft pack``.

.. _`lxd-docker-connectivity-issue`: https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker
.. _`install-multipass`: https://multipass.run/docs/install-multipass
