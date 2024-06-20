Use the flask-framework extension
---------------------------------

The ``flask-framework`` extension requires a ``requirements.txt`` file and a
``app.py`` file that exposes ``app`` as a WSGI app. For example, ``app.py``:

.. literalinclude:: ../code/use-flask-extension/example/app.py
    :language: python

And ``requirements.txt``:

.. literalinclude:: ../code/use-flask-extension/example/requirements.txt

To employ it, include ``extensions: [ flask-framework ]`` in your
``rockcraft.yaml`` file.

.. note::
    The Flask extension is compatible with the ``bare`` and ``ubuntu@22.04``
    bases.

Example:

.. literalinclude:: ../code/use-flask-extension/example/rockcraft.yaml
    :language: yaml

:doc:`/tutorials/getting-started-with-rockcraft-for-flask` shows you how to go
from a host with Ubuntu installed to a Flask app running in docker.

Chiseling the Flask rock
------------------------

The OCI image created in the
:doc:`/tutorials/getting-started-with-rockcraft-for-flask` tutorial is roughly
159MB in size. This can be reduced by using a ``bare`` base. Change the ``base``
to ``bare`` and include a ``build-base`` in ``rockcraft.yaml``:

.. literalinclude:: ../code/use-flask-extension/chiseled-example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:base-start]
    :end-before: [docs:base-end]

Now the OCI image is just 130MB in size.

Managing project files with the Flask extension
-----------------------------------------------

By default the Flask extension only includes ``app.py``, ``static/``,
``app/``, ``templates/`` and ``migrate.sh`` in the Flask project. You can
overwrite this behaviour with a prime declaration in the specially-named
``flask-framework/install-app`` part to instruct the Flask extension on which
files to include or exclude from the project directory in the rock image.

The extension places the files from the project folder in the ``/flask/app``
directory in the final image - therefore, all inclusions and exclusions must
be prefixed with ``flask/app``.

For example, to include only select files:

.. literalinclude:: ../code/use-flask-extension/prime-example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]

To exclude certain files from the project directory in the rock image and
include everything else, add the following part to ``rockcraft.yaml``:

.. literalinclude:: ../code/use-flask-extension/prime_exclude_example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]

Including additional debs in the OCI image
------------------------------------------

if your app requires debs, for example to connect to a database, add the
following snippet to the ``rockfile.yaml``:

.. literalinclude:: ../code/use-flask-extension/deb-example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]

Update Flask app
----------------

After completing the :doc:`/tutorials/getting-started-with-rockcraft-for-flask`
tutorial, let's say you want to add a new endpoint to your Flask application
``/time`` which returns the current time:

.. literalinclude:: ../code/use-flask-extension/update-example/app.py
    :language: python
    :start-after: [docs:time-enpoint-start]
    :end-before: [docs:time-enpoint-end]

Update the version in ``rockcraft.yaml``:

.. literalinclude:: ../code/use-flask-extension/update-example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:version-start]
    :end-before: [docs:version-end]

Pack and deploy the new rock and send a request to the ``/time`` endpoint:

.. literalinclude:: ../code/use-flask-extension/task.yaml
    :language: bash
    :start-after: [docs:update-app-start]
    :end-before: [docs:update-app-end]
    :dedent: 2

The ``curl`` command should return the current time.

View the logs
-------------

To retrieve the logs for the follow app:

.. literalinclude:: ../code/use-flask-extension/example/app.py
    :language: python

With ``requirements.txt``:

.. literalinclude:: ../code/use-flask-extension/example/requirements.txt

And ``rockcraft.yaml``:

.. literalinclude:: ../code/use-flask-extension/example/rockcraft.yaml
    :language: yaml

Run the following steps to get the app running in docker:

.. literalinclude:: ../code/use-flask-extension/task.yaml
    :language: bash
    :start-after: [docs:logs-app-setup-start]
    :end-before: [docs:logs-app-setup-end]
    :dedent: 2

Retrieve the logs using:

.. literalinclude:: ../code/use-flask-extension/task.yaml
    :language: bash
    :start-after: [docs:logs-app-start]
    :end-before: [docs:logs-app-end]
    :dedent: 2

This will show all the logs for the ``flask`` service running in the container.
