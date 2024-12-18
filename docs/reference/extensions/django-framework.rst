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
Gunicorn workers.

Project requirements
====================

There are 2 requirements to be able to use the ``django-framework`` extension:

1. There must be a ``requirements.txt`` file in the root directory of the
   project with ``Django`` declared as a dependency.
2. The project must be named the same as the ``name`` in ``rockcraft.yaml`` with
   any ``-`` replaced by ``_``, i.e., the ``manage.py`` must be located at
   ``./<Rock name with - replaced by _>/<Rock name with - replaced by _>/manage.py``
   relative to the ``rockcraft.yaml`` file.

For the project to make use of asynchronous Gunicorn workers:

- The ``requirements.txt`` file must include ``gevent`` as a dependency.


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

.. _django-gunicorn-worker-selection:

Gunicorn worker selection
=========================

If the project has gevent as a dependency, Rockcraft automatically updates the
pebble plan to spawn asynchronous Gunicorn workers.

When the project instead needs synchronous workers, you can override the worker
type by adding ``--args django sync`` to the Docker command that launches the
rock:

.. code-block:: bash

   docker run --name django-container -d -p 8000:8000 django-image:1.0 \
   --args django sync

Useful links
============

- :ref:`build-a-rock-for-a-django-application`
