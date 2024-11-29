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
``django-framework/async-dependencies`` to the ``rockcraft.yaml``.
Read more :ref:`django-framework/async-dependencies <django-async-deps>`.

If you define
``django-framework/async-dependencies`` you can not
also include ``django-framework/dependencies``.
Running ``rockcraft pack`` will result in an ``Cannot have both sync and async
dependencies. https://bit.ly/flask-async-doc`` error if you try to
use both at the same time.

Project requirements
====================

There are 2 requirements to be able to use the ``django-framework`` extension:

1. There must be a ``requirements.txt`` file in the root directory of the
   project with ``Django`` declared as a dependency.
2. The project must be named the same as the ``name`` in ``rockcraft.yaml`` with
   any ``-`` replaced by ``_``, i.e., the ``manage.py`` must be located at
   ``./<Rock name with - replaced by _>/<Rock name with - replaced by _>/manage.py``
   relative to the ``rockcraft.yaml`` file.

.. _django-sync-deps:

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

.. _django-async-deps:

``parts`` > ``django-framework/async-dependencies``
===================================================

In order to use asynchronous Gunicorn workers, you need
to include ``django-framework/async-dependencies`` in the
``rockcraft.yaml`` while removing
``django-framework/dependencies``.

In the ``rockcraft.yaml``, add the following lines:

.. code-block:: yaml

  parts:
    django-framework/async-dependencies:
      python-packages:
        - gunicorn[gevent]

If your project needs additional debs to run, you can add them to
``stage-packages``.

.. code-block:: yaml

  parts:
    django-framework/async-dependencies:
      python-packages:
        - gunicorn[gevent]
      stage-packages:
        # list required packages or slices for your Django application below.
        - libpq-dev

.. warning::
  You can use either ``django-framework/async-dependencies`` or
  ``django-framework/dependencies``, but not both at the same time.
  To read more about synchronous dependencies,
  see :ref:`django-framework/dependencies <django-sync-deps>`.


Useful links
============

- :ref:`build-a-rock-for-a-django-application`
