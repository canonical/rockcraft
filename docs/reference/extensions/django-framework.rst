.. _django-framework-reference:

django-framework
----------------

The Django extension streamlines the process of building Django application
rocks.

It facilitates the installation of Django application dependencies, including
Gunicorn, inside the rock. Additionally, it transfers your project files to
``/django/app`` within the rock.

A statsd-exporter is installed alongside the Gunicorn server to export Gunicorn
server metrics.

.. note::
    The Django extension is compatible with the ``bare``, ``ubuntu@22.04``
    and ``ubuntu@24.04`` bases.

The Django extension supports both synchronous and asynchronous
Gunicorn workers. If you want asynchronous workers, you have to add
the ``gevent`` package to the ``requirements.txt`` file.
Read more :ref:`Using asynchronous Gunicorn workers <async-gunicorn-workers>`.

Project requirements
====================

There are 2 requirements to be able to use the ``django-framework`` extension:

1. There must be a ``requirements.txt`` file in the root directory of the
   project with ``Django`` declared as a dependency.
2. The project must be named the same as the ``name`` in ``rockcraft.yaml`` with
   any ``-`` replaced by ``_``, i.e., the ``manage.py`` must be located at
   ``./<Rock name with - replaced by _>/<Rock name with - replaced by _>/manage.py``
   relative to the ``rockcraft.yaml`` file.


``parts`` > ``django-framework/dependencies:`` > ``stage-packages``
===================================================================

You can use this key to specify any dependencies required for your Django
application. In the following example we use it to specify ``libpq-dev``:

.. code-block:: yaml

  parts:
    django-framework/dependencies:
      stage-packages:
        # list required packages or slices for your Django application below.
        - libpq-dev

.. _async-gunicorn-workers:

Using asynchronous Gunicorn workers
===================================

If you want to use asynchronous workers, you have to add the ``gevent`` package
to the ``requirements.txt`` file. Rockcraft automatically detects this and
updates the Pebble plan to use the asynchronous workers. If you have ``gevent``
installed in your rock but decided to use ``sync`` workers instead you can do
so by using the ``--args`` parameter of Docker:

.. code-block:: shell
  :caption: Use sync workers instead of gevent
   $ docker run \
       --name django-container \
       -d -p 8138:8000 \
       django-image:1.0 \
       --args django sync


.. note::
    The Django extension is compatible with the ``bare``, ``ubuntu@22.04`` and
    ``ubuntu@24.04`` bases.

Useful links
============

- :ref:`build-a-rock-for-a-django-application`
