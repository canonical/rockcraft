.. _how_to_build_docs:

How to build the documentation
******************************

Use the provided ``tox.ini`` to install the documentation requirements and
build the documentation:

.. literalinclude:: code/build-docs/task.yaml
    :language: bash
    :start-after: [docs:build-docs]
    :end-before: [docs:build-docs-end]
    :dedent: 2

Even better, serve it locally on port 8080. The documentation will be rebuilt
on each file change, and will reload the browser view.

.. literalinclude:: code/build-docs/task.yaml
    :language: bash
    :start-after: timeout -s SIGINT
    :end-before: [docs:build-autobuild-end]
    :dedent: 2

Note that ``tox`` automatically creates and activates the virtual environment.
