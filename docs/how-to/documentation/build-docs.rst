.. _how-to-build-the-documentation:

Build the documentation
=======================

Clone the Rockcraft repository and run the following commands from the
repository root, not from the ``docs/`` directory.

To build the documentation locally, ensure that ``make`` and ``python3-venv``
are installed on your system. The ``make setup-docs`` command creates the
documentation virtual environment automatically.

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

Even better, serve it on :literalref:`http://127.0.0.1:8000/`. The documentation will be rebuilt
on each file change, and will reload the browser view.

.. literalinclude:: ../code/build-docs/task.yaml
    :language: bash
    :start-after: timeout -s SIGINT
    :end-before: [docs:make-rundocs-end]
    :dedent: 2

Note that ``make docs-auto`` automatically activates the virtual environment,
as long as it already exists.

To check the documentation for problems locally, run ``make docs-lint`` from the
repository root. If you want to inspect the documentation subproject targets
directly, run ``make help`` from the ``docs/`` directory.
