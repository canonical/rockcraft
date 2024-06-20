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
