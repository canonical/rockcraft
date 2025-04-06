Adding Parts to a rock
**********************

Project setup
-------------

In the previous step we created a rootless rock that did not
need privileges to expose a basic HTML file with NGINX. However,
our service was exposed via HTTP, which is not encrypted and less
secure.

In this step we will add a new part to the ``rockcraft.yaml`` in
order to create SSL certificates to expose our HTML file with HTTP
over TLS (HTTPS).

At this point, our directory structure should look like this:

.. code-block:: text

    .
    ├─ rockcraft.yaml
    ├─ nginx.conf
    └─ index.html

    3 files

We will not be making any changes to it, but to the contents of
``nginx.conf`` and ``rockcraft.yaml``.


Set up SSL in Nginx configuration
---------------------------------

To serve our web content via HTTPS we will need to change our
Nginx configuration to listen to the ``443`` port and point to
some SSL certificates that will be generated afterwards:

.. literalinclude:: code/add-parts/nginx.conf
    :caption: nginx.conf
    :language: nginx

Note that we have two servers declared now, the first one listens
to any requests to ``localhost`` on port 80 and redirects them
to the same location through ``https``.

The second server will be the one picking up the redirected requests
and serving our static files at ``var/www/html``. To do so, a SSL key
and certificate must be emmited by a root certificate authority (CA).


Domain verification
===================

In order to have a certificate emmited by a CA, we would need to have a
domain pointing to the IP address where our server lives. However, since
we don't have such domain, we can overcome that limitation by generating
our own self-signed SSL certificate.

.. warning::

    self-signed certificates are used for development purposes and will
    be detected by browsers as not valid. When deploying a web service
    to the internet, an actual certificate signed by CA should be used.
    You can read more about the domain verification process in
    `letsencrypt docs`_.

Self-signed SSL certificates can be easily generated with tools like
``openssl``, but we will use `minica`_ to better emulate the process of
requesting a certificate from a CA, as well as showcasing how to build
and use a ``go`` package within the rocks build process.


Generating SSL certificates
---------------------------

To have our self-signed SSL certificates generated using ``minica``, we
will first add a new ``part`` that compiles the ``go`` library for later
use. To do so, we will use the ``plugin: go`` directive, and specify the
``source`` pointing to the ``minica`` git repository.

After that part, we can have another part to actually generate the
certificates, using the compiled ``minica`` binary. We will declare that
this new part must run ``after`` compiling the go module, then we will
use ``override-build`` to run ``minica`` and have our key and certificate
generated inside the directory where our nginx configuration expects them:

.. literalinclude:: code/add-parts/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

Note that we also include a ``override-prime`` directive to set the owner
of the folder containing the certificates. This is because the rock is
rootless, and nginx would not be able to access the files, since they
are owned by ``root`` by default.


Pack the rock with Rockcraft
----------------------------

Once everything is set up, we just need to pack the rock with rockcraft
and copy it to the docker daemon to use it later on:

.. literalinclude:: code/add-parts/task.yaml
    :language: bash
    :start-after: [docs:build-and-copy-rock]
    :end-before: [docs:build-and-copy-rock-end]
    :dedent: 2

Run the rock with docker
------------------------

Once packed and copied you can now run the rock using docker. Note that
you will need to bind both HTTP and HTTPS ports to access the page:

.. literalinclude:: code/add-parts/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

Once the container is running (you can check with ``docker ps``) you can
open the page in your browser or use ``curl``:

.. literalinclude:: code/add-parts/task.yaml
    :language: bash
    :start-after: [docs:test-rock]
    :end-before: [docs:test-rock-end]
    :dedent: 2

note that you will be redirected when using ``HTTP``, since we configured
that previously for Nginx:

.. code-block:: text

    <html>
    <head><title>301 Moved Permanently</title></head>
    <body>
    <center><h1>301 Moved Permanently</h1></center>
    <hr><center>nginx/1.24.0 (Ubuntu)</center>
    </body>
    </html>

If using ``curl``, you can specify the ``-L`` option to follow the
redirection, or use ``https://`` instead of ``http://`` when making
the request:

.. literalinclude:: code/add-parts/task.yaml
    :language: bash
    :start-after: [docs:test-rock-redirection]
    :end-before: [docs:test-rock-redirection-end]
    :dedent: 2

.. note::

    Since the certificates are self-signed and hence, invalid, you will
    get a warning page in your browser. If using curl, it will throw an
    error unless you pass ``-k`` option, which allows access to insecure
    sites.

The output should now be the contents of ``index.html``:

.. literalinclude:: code/baseless-rock/index.html
    :language: text

.. _letsencrypt docs: https://letsencrypt.org/how-it-works/
.. _minica: https://github.com/jsha/minica
