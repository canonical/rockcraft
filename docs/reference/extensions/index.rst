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

.. toctree::
    :maxdepth: 1

    flask-framework
    django-framework
    fastapi-framework
    go-framework
    express-framework
    spring-boot-framework
