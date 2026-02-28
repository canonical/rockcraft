.. _reference-flask-framework:

Flask framework
===============

The Flask extension streamlines the process of building Flask application rocks.

It facilitates the installation of Flask application dependencies, including
Gunicorn, inside the rock. Additionally, it transfers your project files to
``/flask/app`` within the rock.
By default, the base ``bare`` is used to generate a lightweight image.

.. note::
    The Flask extension is compatible with the ``bare``, ``ubuntu@22.04``
    and ``ubuntu@24.04`` bases.

The Flask extension supports both synchronous and asynchronous
Gunicorn workers.

.. _reference-flask-framework-project-requirements:

Project requirements
--------------------

There are 2 requirements to be able to use the ``flask-framework`` extension:

1. There must be a ``requirements.txt``  or ``pyproject.toml`` file in the root of the project with
   ``Flask`` declared as a dependency
2. The project must include a WSGI app with the path ``app:app``. This means
   there must be an ``app.py`` file at the root of the project with the name
   of the Flask object is set to ``app``.

For the project to make use of asynchronous Gunicorn workers:

- The ``requirements.txt`` or ``pyproject.toml`` file must include ``gevent`` as a dependency.

.. _reference-flask-framework-stage-packages:

``parts`` > ``flask-framework/dependencies`` > ``stage-packages``
-----------------------------------------------------------------

You can use this key to specify any dependencies required for your Flask
application. In the following example we use it to specify ``libpq-dev``:

.. code-block:: yaml
  :caption: rockcraft.yaml

  parts:
    flask-framework/dependencies:
      stage-packages:
        # list required packages or slices for your flask app below.
        - libpq-dev

.. _reference-flask-framework-statsd-exporter:

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
    - ``flask_response_code``
  * - ``gunicorn.requests``
    - ``flask_requests``
  * - ``gunicorn.request.duration``
    - ``flask_request_duration``

The  exporter listens on localhost at port 9125. You can push your
own metrics to the exporter using any StatsD client. This snippet from an example
Flask app uses pystatsd as a client:

.. code-block:: python

  import statsd
  c = statsd.StatsClient('localhost', 9125)
  c.incr('my_counter')


See the `StatsD exporter documentation <https://github.com/prometheus/statsd_exporter>`_
for more information.


.. _flask-gunicorn-worker-selection:

Gunicorn worker selection
-------------------------

If the project has gevent as a dependency, Rockcraft automatically updates the
pebble plan to spawn asynchronous Gunicorn workers.

When the project instead needs synchronous workers, you can override the worker
type by adding ``--args flask sync`` to the Docker command that launches the
rock:

.. code-block:: bash

   docker run --name flask-container -d -p 8000:8000 flask-image:1.0 \
   --args flask sync

.. _reference-flask-framework-prime:

``parts`` > ``flask-framework/install-app`` > ``prime``
-------------------------------------------------------

You can use this field to specify the files to be included or excluded from
your rock upon ``rockcraft pack``. Follow the ``flask/app/<filename>``
notation. For example:

.. code-block:: yaml
  :caption: rockcraft.yaml

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
------------

:ref:`tutorial-build-a-rock-for-a-flask-app`
