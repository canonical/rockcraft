Manage project files with the Flask extension
---------------------------------------------

Rockcraft offers a ``flask-framework``
:ref:`extension <flask-framework-reference>` to facilitate the containerisation
of your Flask application as a rock.

See the tutorial :doc:`/tutorials/getting-started-with-flask` for a
comprehensive set of steps that guide you through the creation and
containerisation of a Flask application, from scratch, using Rockcraft and this
``flask-framework`` :ref:`extension <flask-framework-reference>`


----

By default the Flask extension only includes ``app.py``, ``static/``,
``app/``, ``templates/`` and ``migrate.sh`` in the Flask project. You can
overwrite this behaviour with a prime declaration in the specially-named
``flask-framework/install-app`` Rockcraft part to instruct the Flask extension on which
files to include or exclude from the project directory when building the rock.

The extension places the files from the project folder in the ``/flask/app``
directory in the final image - therefore, all inclusions and exclusions must
be prefixed with ``flask/app``.

For example, to include only select files:

.. literalinclude:: ../code/manage-flask-extension-rock-contents/prime-example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]

To exclude certain files from the project directory when building the rock,
while including everything else, add the following part to ``rockcraft.yaml``:

.. literalinclude:: ../code/manage-flask-extension-rock-contents/prime-exclude-example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]

Including additional packages in the rock
=========================================

If your app requires additional dependencies (.e.g. to connect to a
database), you can add and adjust the following snippet to the
``rockcraft.yaml`` file, according to your application needs:

.. literalinclude:: ../code/manage-flask-extension-rock-contents/deb-example/rockcraft.yaml
    :language: yaml
    :start-after: [docs:parts-start]
    :end-before: [docs:parts-end]
