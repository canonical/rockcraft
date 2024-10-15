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

Project requirements
====================

There are 2 requirements to be able to use the ``flask-framework`` extension:

1. There must be a ``requirements.txt`` file in the root of the project with
   ``Flask`` declared as a dependency
2. The project must include a WSGI app in a variable called ``app`` in one of
   the following files relative to the project root (in order of priority):

   * ``app.py``
   * ``main.py``
   * ``__init__.py``, ``app.py`` or ``main.py`` within the ``app`` or ``src``
     directory or within a directory with the name of the rock as declared in
     ``rockcraft.yaml``.

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
