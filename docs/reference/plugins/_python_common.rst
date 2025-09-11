
Dependencies
------------

Since none of the bases that are available for rocks contain a default Python
installation, including a Python interpreter in Rockcraft projects is mandatory.
Both the ``python`` and the ``poetry`` plugins also require the ``venv`` module
to create the virtual environment where Python packages are installed at build
time.

The easiest way to do this is to include the ``python3-venv`` package in the
``stage-packages`` of the part that uses the Python-based plugin. This will pull
in the default Python interpreter for the ``build-base``, like Python 3.10 for
Ubuntu 22.04. However, other versions can be used by explicitly declaring them -
here's an example that uses ``python3.12-venv`` from the Deadsnakes ppa:

.. code-block:: yaml
  :caption: rockcraft.yaml

   package-repositories:
     - type: apt
       ppa: deadsnakes/ppa
       priority: always

   parts:
     my-part:
       plugin: <python or poetry or uv>
       source: .
       stage-packages: [python3.12-venv]
