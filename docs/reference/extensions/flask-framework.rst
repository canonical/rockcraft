.. _flask-framework-reference:

flask-framework
---------------

The Flask extension streamlines the process of building Flask application rocks.

It facilitates the installation of Flask application dependencies, including
Gunicorn, inside the rock. Additionally, it transfers your project files to
``/flask/app`` within the rock.

A statsd-exporter is installed alongside the Gunicorn server to export Gunicorn
server metrics.

.. note::
    The Flask extension is compatible with the ``bare``, ``ubuntu@22.04``
    and ``ubuntu@24.04`` bases.

The Flask extension supports both synchronous and asynchronous
Gunicorn workers. If you want asynchronous workers, you have to add
``gevent`` package to the ``requirements.txt`` file.
Read more
:ref:`Using asynchronous Gunicorn workers <flask-async-gunicorn-workers>`.

Project requirements
====================

There are 2 requirements to be able to use the ``flask-framework`` extension:

1. There must be a ``requirements.txt`` file in the root of the project with
   ``Flask`` declared as a dependency
2. The project must include a WSGI app with the path ``app:app``. This means
   there must be an ``app.py`` file at the root of the project with the name
   of the Flask object is set to ``app``

``parts`` > ``flask-framework/dependencies`` > ``stage-packages``
=================================================================

You can use this key to specify any dependencies required for your Flask
application. In the following example we use it to specify ``libpq-dev``:

.. code-block:: yaml

  parts:
    flask-framework/dependencies:
      stage-packages:
        # list required packages or slices for your flask app below.
        - libpq-dev

.. _flask-async-gunicorn-workers:

Using asynchronous Gunicorn workers
===================================

If you want to use asynchronous workers, you have to add ``gevent`` package to
the ``requirements.txt`` file. Rockcraft automatically detects this and updates
the pebble plan to use the asynchronous workers. If you have ``gevent``
installed in your rock but decided to use ``sync`` workers instead you can use
the ``--args`` parameter of ``docker run`` to use ``sync`` workers instead of
the default ``gevent``:

.. code-block:: shell
  :caption: Use sync workers instead of gevent
   $ docker run \
       --name flask-container \
       -d -p 8138:8000 \
       flask-image:1.0 \
       --args flask sync

``parts`` > ``flask-framework/install-app`` > ``prime``
=======================================================

You can use this field to specify the files to be included or excluded from
your rock upon ``rockcraft pack``. Follow the ``flask/app/<filename>``
notation. For example:

.. code-block:: yaml

  parts:
    flask-framework/install-app:
      prime:
        - flask/app/.env
        - flask/app/app.py
        - flask/app/webapp
        - flask/app/templates
        - flask/app/static

Some files, if they exist, are included by default. These include:
``app``, ``app.py``, ``migrate``, ``migrate.sh``, ``migrate.py``, ``static``,
``templates``.

Useful links
============

- :ref:`build-a-rock-for-a-flask-application`
