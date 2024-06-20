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
following snippet to the `rockfile.yaml`:

.. literalinclude:: ../code/use-flask-extension/deb-example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]
