Use the django-framework extension
----------------------------------

.. note::
    The Django extension is compatible with the ``bare`` and ``ubuntu@22.04``
    bases.

To employ it, include ``extensions: [ django-framework ]`` in your
``rockcraft.yaml`` file.

Example:

.. literalinclude:: code/use-django-extension/example/rockcraft.yaml
    :language: yaml

Managing project files with the Django extension
------------------------------------------------

The extension will search for a directory named after the rock within the
Rockcraft project directory to transfer it into the rock image. The Django
project should have a directory named after the rock, and the ``wsgi.py``
file within this directory must contain an object named ``application``
to serve as the WSGI entry point.

The following is a typical Rockcraft project that meets this requirement.

.. code-block::

    +-- example_django
    |   |-- example_django
    |   |   |-- wsgi.py
    |   |   +-- ...
    |   |-- manage.py
    |   |-- migrate.sh
    |   +-- some_app
    |       |-- views.py
    |       +-- ...
    |-- requirements.txt
    +-- rockcraft.yaml

To override this behaviour and adopt a different project structure, add
the ``django-framework/install-app`` part to install the Django project in
the ``/django/app`` directory within the rock image and update the command
for the ``django`` service to point to the WSGI path of your project.

.. literalinclude:: code/use-django-extension/override_example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]
