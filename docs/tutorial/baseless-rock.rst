Create a baseless rock
**********************

Project setup
-------------

We will keep expanding from the previous sections. In this case,
we are going to lower the disk usage of our rock by "chiselling"
it into slices.

Chiselling a rock comes with more advantages other than reducing
the size of the resulting artifact, it can also help reduce the
vulnerabilities by removing unnecessary dependencies. Rockcraft
natively support this feature by integrating the Chisel tool.
See :ref:`chisel_explanation` for more details.

At this point on the tutorial, we should have already created
three files:

.. code-block:: text

    .
    ├─ rockcraft.yaml
    ├─ nginx.conf
    └─ index.html

    3 files

We previously managed to serve the ``index.html`` via HTTP using
Nginx. However, ``nginx`` service is not really required,
as rocks use :doc:`Pebble </explanation/pebble>` instead of
``Systemd`` and when running containerized, we specify the
``daemon off;`` flag when running nginx. Thus, we don't need
the entire ``nginx`` package, but a part (or a ``slice``) from it.

Install Chisel slices
---------------------

By "chiselling" a rock we can obtain a "baseless" image as a result,
this is an image with no base. This is because we are no longer
installing packages, but Chisel slices, and thus ``apt`` and ``dpkg``
are not needed, so we can set the ``base`` field as ``bare``.

Chisel slices are declared the same way as a stage-package in
``rockcraft.yaml`` as long as such slice exists in `Chisel releases`_:

.. _chisel-example:

.. literalinclude:: code/baseless-rock/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

Note that, appart from the ``nginx_bins`` slice, we also needed some
base slices: ``base-files_var``, ``base-files_home``, ``base-passwd_data``.
This is because the ``base`` is bare and as such, it does not contain
some files and directories that nginx read from, like ``/etc/passwd`` or
``/run/``.

Pack the rock with Rockcraft
----------------------------

Once everything is set up, we just need to pack the rock with rockcraft
and copy it to the docker daemon to use it later on:

.. literalinclude:: code/baseless-rock/task.yaml
    :language: bash
    :start-after: [docs:build-and-copy-rock]
    :end-before: [docs:build-and-copy-rock-end]
    :dedent: 2

Now lets see what happens when we run ``docker image ls``:

.. code-block:: text

    REPOSITORY                TAG       IMAGE ID       CREATED          SIZE
    chiselled-hello-nginx     latest    1a9b733978a0   5 minutes ago    21.5MB
    hello-nginx               latest    8f853c7fd983   2 days ago       146MB

As you can see, the size of the image has been dramatically
reduced after chiselling the initial rock.

Run the rock with docker
------------------------

Once packed and copied you can now run the rock using docker. Note that
you will need to bind the ports to access the page via HTTP:

.. literalinclude:: code/baseless-rock/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Once the container is running (you can check with ``docker ps``) you should
be able to see the HTML page in your browser, or using curl:

.. literalinclude:: code/baseless-rock/task.yaml
    :language: bash
    :start-after: [docs:test-rock]
    :end-before: [docs:test-rock-end]
    :dedent: 2

The output should be the contents of ``index.html``:

.. literalinclude:: code/baseless-rock/index.html
    :language: text
