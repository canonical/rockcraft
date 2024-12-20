.. _how_to_build_docs:

How to build the documentation
******************************

Use the provided ``Makefile`` to install the documentation requirements:

.. literalinclude:: ../code/build-docs/task.yaml
    :language: bash
    :start-after: [docs:install-deps]
    :end-before: [docs:install-deps-end]
    :dedent: 2

Once the requirements are installed, you can use the provided ``Makefile`` to
build the documentation:

.. literalinclude:: ../code/build-docs/task.yaml
    :language: bash
    :start-after: [docs:make-docs]
    :end-before: [docs:make-docs-end]
    :dedent: 2

Even better, serve it locally on port 8080. The documentation will be rebuilt
on each file change, and will reload the browser view.

.. literalinclude:: ../code/build-docs/task.yaml
    :language: bash
    :start-after: timeout -s SIGINT
    :end-before: [docs:make-rundocs-end]
    :dedent: 2

Note that ``make docs-auto`` automatically activates the virtual environment,
as long as it already exists.
