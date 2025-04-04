Install packages in a rock
**************************

Project setup
-------------

We will use the setup from the previous section, where we created
a rock containing a simple ``index.html`` file. So this is the
directory structure that will serve as a base for this section:

.. code-block:: text

    .
    ├─ rockcraft.yaml
    └─ index.html

    2 files

Using this we managed to add the ``index.html`` inside our rock, but
we could not serve it to the outside world via HTTP. So this is what
we will achieve at the end of this section.

Create Nginx configuration
--------------------------

First of all, we need to create a configuration file to tell Nginx
where our server files can be found in order to be served. To do so,
open a new editor and write:

.. literalinclude:: code/install-packages/nginx.conf
    :caption: nginx.conf
    :language: nginx

This file will tell Nginx that our html is found under ``var/www/html``,
and the index of the page is ``index.html``. Now the next step is
adding this to our rock.

Install and setup Nginx inside the rock
---------------------------------------

To install ``nginx`` inside our rock, we just need to declare it under
:ref:`stage_packages`, so it is installed during the stage step, making
it available to use in the final image.

Since we now need to include the files under a different location, we will
use the :ref:`organize` directive instead of :ref:`stage`. This way, we can
specify the path where we want our files to be copied when moving from the
build step to the stage step.

The resulting ``rockcraft.yaml`` looks like this:

.. literalinclude:: code/install-packages/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

Note that we have added a service to serve as the rock
entrypoint.

Pack the rock with Rockcraft
----------------------------

Once everything is set up, we just need to pack the rock with rockcraft
and copy it to the docker daemon to use it later on:

.. literalinclude:: code/install-packages/task.yaml
    :language: bash
    :start-after: [docs:build-and-copy-rock]
    :end-before: [docs:build-and-copy-rock-end]
    :dedent: 2

Run the rock with docker
------------------------

Once packed and copied you can now run the rock using docker. Note that
you will need to bind the ports to access the page via HTTP:

.. literalinclude:: code/install-packages/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Once the container is running (you can check with ``docker ps``) you should
be able to see the HTML page in your browser, or using curl:

.. literalinclude:: code/install-packages/task.yaml
    :language: bash
    :start-after: [docs:test-rock]
    :end-before: [docs:test-rock-end]
    :dedent: 2

The output should be the contents of ``index.html``:

.. literalinclude:: code/install-packages/index.html
    :language: text
