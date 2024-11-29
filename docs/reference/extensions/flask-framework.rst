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
``flask-framework/async-dependencies`` to the ``rockcraft.yaml``.
Read more :ref:`flask-framework/async-dependencies <flask-async-deps>`.

If you define
``flask-framework/async-dependencies`` you can not
also include ``flask-framework/dependencies``.
Running ``rockcraft pack`` will result in an ``Cannot have both sync and async
 dependencies. https://bit.ly/flask-async-doc`` error if you try to
use both at the same time.

Project requirements
====================

There are 2 requirements to be able to use the ``flask-framework`` extension:

1. There must be a ``requirements.txt`` file in the root of the project with
   ``Flask`` declared as a dependency
2. The project must include a WSGI app with the path ``app:app``. This means
   there must be an ``app.py`` file at the root of the project with the name
   of the Flask object is set to ``app``

.. _flask-sync-deps:

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

.. _flask-async-deps:

``parts`` > ``flask-framework/async-dependencies``
=================================================================

In order to use asynchronous Gunicorn workers, you need
to include ``flask-framework/async-dependencies`` in the
``rockcraft.yaml`` while removing
``flask-framework/dependencies``.

In the ``rockcraft.yaml``, add the following lines:

.. code-block:: yaml

  parts:
    flask-framework/async-dependencies:
      python-packages:
        - gunicorn[gevent]

If your project needs additional debs to run, you can add them to
``stage-packages``.

.. code-block:: yaml

  parts:
    flask-framework/async-dependencies:
      python-packages:
        - gunicorn[gevent]
      stage-packages:
        # list required packages or slices for your Flask application below.
        - libpq-dev

.. warning::
  You can use either ``flask-framework/async-dependencies`` or
  ``flask-framework/dependencies``, but not both at the same time.
  To read more about synchronous dependencies,
  see :ref:`flask-framework/dependencies <flask-sync-deps>`.

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
