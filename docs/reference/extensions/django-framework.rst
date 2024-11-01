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

1. ``Django`` needs to be declared as a requirement either in a
   ``requirements.txt`` file or within another ``pip`` supported
   requirement (eg. via ``pyproject.toml``).
2. The project must be named the same as the ``name`` in ``rockcraft.yaml`` with
   any ``-`` replaced by ``_``, i.e., the ``manage.py`` must be located at
   ``./<Rock name with - replaced by _>/<Rock name with - replaced by _>/manage.py``
   relative to the ``rockcraft.yaml`` file.

Useful links
============

- :ref:`build-a-rock-for-a-django-application`
