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

.. warning::
  You can only use 1 of the dependencies parts at a time.

``parts`` > ``django-framework/async-dependencies``
=================================================================

You can use this key to specify that you want to use async gunicorn workers in
your Django application. It also works just like ``django-framework/dependencies``.

Just uncomment the following lines:
.. code-block:: yaml

  parts:
    django-framework/async-dependencies:
      python-packages:
        - gunicorn[gevent]

If your project needs additional debs to run, you can add them to
``stage-packages`` just like it is done in ``django-framework/dependencies``.

.. warning::
  You can only use 1 of the dependencies parts at a time.

Useful links
============

- :ref:`build-a-rock-for-a-django-application`
