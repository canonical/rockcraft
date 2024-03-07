Use the flask-framework extension
---------------------------------

The Flask extension is compatible with the ``bare`` and ``ubuntu@22.04`` bases.
To employ it, include ``extensions: [ flask-framework ]`` in your
``rockcraft.yaml`` file.

Example:

.. literalinclude:: code/use-flask-extension/example/rockcraft.yaml
    :language: yaml

Managing project files with the flask extension
-----------------------------------------------

By default the flask extension only includes the ``app.py``, ``static/``,
``app/``, and ``templates/`` in the flask project. But you can overwrite this
behaviour with a prime declaration in the specially-named
``flask-framework/install-app`` part to instruct the flask extension on which
files to include or exclude from the project directory in the rock image.

The extension places the files from the project folder in the ``/flask/app``
directory in the final image - therefore, all inclusions and exclusions must
be prefixed with ``flask/app``.

For example, to include only select files:

.. literalinclude:: code/use-flask-extension/prime_example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]

To exclude certain files from the project directory in the rock image,
add the following part to ``rockcraft.yaml``:

.. literalinclude:: code/use-flask-extension/prime_exclude_example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]
