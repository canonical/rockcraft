.. meta::
    :description: The reference documentation for all extensions in Rockcraft.

.. _reference-extensions:

Extensions
==========

Extensions are reusable configuration fragments that simplify a
``rockcraft.yaml`` file for common application frameworks. An extension
configures the parts, services, and other keys needed to build and run the
application, while still allowing you to customize the generated
configuration in the project file.

The top-level ``extensions`` key in ``rockcraft.yaml`` defines the extension
used by the project. When Rockcraft loads the project, it expands the extension
and combines its configuration with your project file.

.. _reference-extensions-ubuntu-2604-frameworks:

Ubuntu 26.04 framework extensions
---------------------------------

The Express, FastAPI, Go, Flask, and Django framework extensions are stable on their
supported bases earlier than Ubuntu 26.04 LTS. The Spring Boot extension remains
experimental on its supported bases, and the Ubuntu 26.04 implementations of all
six extensions are experimental. To use one of these extensions with Ubuntu 26.04,
set ``ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1`` when running Rockcraft.

Rockcraft selects the extension implementation from ``build-base`` when it is set, or from ``base`` otherwise. For a rock with ``base: bare``, ``build-base`` is mandatory. For example,
``base: bare`` with ``build-base: ubuntu@24.04`` uses the stable extension
implementation and doesn't require the experimental extensions environment
variable. For migration guidance, see
:ref:`how-to-migrate-2604`.

On Ubuntu 26.04, these six extensions place application content under
``/app`` and create ``/app-data`` for application-generated data.
``/app-data`` is owned by ``_daemon_`` and is writable by the application
service. Use it as the persistent-at-runtime application data directory,
rather than for the application content installed under ``/app``.

``/app-data`` is part of the image's container filesystem. Its contents don't
persist across container replacement unless a volume is mounted at that path.

.. toctree::
    :maxdepth: 1

    flask-framework
    django-framework
    fastapi-framework
    go-framework
    express-framework
    spring-boot-framework
