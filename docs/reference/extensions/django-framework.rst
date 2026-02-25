.. _reference-django-framework:

Django framework
================

The Django extension streamlines the process of building Django application
rocks.

It facilitates the installation of Django application dependencies, including
Gunicorn, inside the rock. Additionally, it transfers your project files to
``/django/app`` within the rock.
By default, the base ``bare`` is used to generate a lightweight image.

.. note::
    The Django extension is compatible with the ``bare``, ``ubuntu@22.04``
    and ``ubuntu@24.04`` bases.

The Django extension supports both synchronous and asynchronous
Gunicorn workers.

.. _reference-django-framework-project-requirements:

Project requirements
--------------------

There are 2 requirements to be able to use the ``django-framework`` extension:

1. There must be a ``requirements.txt`` or ``pyproject.toml`` file in the root
  directory of the project with ``Django`` declared as a dependency.
2. The Django project directory at the rock root must be named the same as the
  ``name`` in the project file, with any ``-`` replaced by ``_``. The Django
  settings package inside that directory must be either the same name or
  ``mysite``. This means ``manage.py`` is located at
  ``./<rock-name>/<rock-name>/manage.py`` and ``wsgi.py`` is located at
  ``./<rock-name>/<rock-name>/wsgi.py`` or ``./<rock-name>/mysite/wsgi.py``.

For the project to make use of asynchronous Gunicorn workers:

- The ``requirements.txt`` or ``pyproject.toml`` file must include ``gevent`` as a dependency.

.. _reference-django-framework-stage-packages:

``parts`` > ``django-framework/dependencies:`` > ``stage-packages``
-------------------------------------------------------------------

You can use this key to specify any dependencies required for your Django
application. In the following example we use it to specify ``libpq-dev``:

.. code-block:: yaml
   :caption: rockcraft.yaml

   parts:
      django-framework/dependencies:
         stage-packages:
         # list required packages or slices for your Django application below.
         - libpq-dev

.. _reference-django-framework-statsd-exporter:

StatsD exporter
---------------

A StatsD exporter is installed alongside the Gunicorn server to record
server metrics. Some of the `Gunicorn-provided metrics
<https://gunicorn.org/instrumentation/>`_
are mapped to new names:

.. list-table::

  * - Gunicorn metric
    - StatsD metric
  * - ``gunicorn.request.status.*``
    - ``django_response_code``
  * - ``gunicorn.requests``
    - ``django_requests``
  * - ``gunicorn.request.duration``
    - ``django_request_duration``

The  exporter listens on localhost at port 9125. You can push your
own metrics to the exporter using any StatsD client. This snippet from an example
Django app uses pystatsd as a client:

.. code-block:: python

  import statsd
  c = statsd.StatsClient('localhost', 9125)
  c.incr('my_counter')


See the `StatsD exporter documentation <https://github.com/prometheus/statsd_exporter>`_
for more information.


.. _django-gunicorn-worker-selection:

Gunicorn worker selection
-------------------------

If the project has gevent as a dependency, Rockcraft automatically updates the
pebble plan to spawn asynchronous Gunicorn workers.

When the project instead needs synchronous workers, you can override the worker
type by adding ``--args django sync`` to the Docker command that launches the
rock:

.. code-block:: bash

   docker run --name django-container -d -p 8000:8000 django-image:1.0 \
   --args django sync


Useful links
------------

:ref:`tutorial-build-a-rock-for-a-django-app`
