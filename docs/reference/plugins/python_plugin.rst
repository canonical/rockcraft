
.. include:: /common/craft-parts/python_plugin.rst
   :end-before: .. _python-details-begin:

Dependencies
------------

Since none of the bases that are available for rocks contain a default Python
installation, including a Python interpreter in Rockcraft projects is mandatory.
The plugin also requires the ``venv`` module to create the virtual environment
where Python packages are installed at build time.

The easiest way to do this is to include the ``python3-venv`` package in the
``stage-packages`` of the part that uses the Python plugin. This will pull in
the default Python interpreter for the ``build-base``, like Python 3.10 for
Ubuntu 22.04. However, other versions can be used by explicitly declaring them,
such as ``python3.12-venv`` for projects that use the Deadsnakes ppa.

.. include:: /common/craft-parts/python_plugin.rst
   :start-after: .. _python-details-end:
