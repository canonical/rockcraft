
*********
Rockcraft
*********

|snap|  |docs|

Purpose
-------

Tool to create OCI Images using the language from `Snapcraft`_ and `Charmcraft`_.

.. _Snapcraft: https://snapcraft.io

.. _Charmcraft: https://juju.is

Installing
----------

Install Rockcraft from the Snap Store

|Snap Store|

Documentation
-------------

Documentation on the usage of the tool and tutorial can be found on
https://documentation.ubuntu.com/rockcraft/en/stable/


.. |snap| image:: https://snapcraft.io/rockcraft/badge.svg
    :alt: Snap Status
    :target: https://snapcraft.io/rockcraft

.. |docs| image:: https://readthedocs.com/projects/canonical-rockcraft/badge/?version=stable
    :alt: Documentation Status
    :target: https://documentation.ubuntu.com/rockcraft/en/stable/?badge=stable

.. |Snap Store| image:: https://snapcraft.io/static/images/badges/en/snap-store-black.svg
    :alt: Get it from the Snap Store
    :target: https://snapcraft.io/rockcraft



Testing
-------

In addition to unit tests in :code:`tests/unit`, which can be run with :code:`make test-units`,
a number of integrated tests in :code:`tests/spread` can be run with `Spread`_. See the
`general notes`_ and take note of these ``rockcraft``-specific instructions:

* Initialize/update git submodules to fetch Spread-related helper scripts:

  .. code-block::

     $ git submodule init
     $ git submodule update

* Spread needs a ``rockcraft`` snap in order to run. Create one with :code:`snapcraft` via:

  .. code-block::

     $ snapcraft --use-lxd
     $ cp <generated snap> tests/

* Run Spread:

  .. code-block::

     $ spread tests/spread
     # Or run a specific test
     $ spread tests/spread/tutorial/basic
     # Use "-v" for verbose, and "-debug" to get a shell if the test fails
     $ spread -v -debug tests/spread/tutorial/basic

.. _Spread: https://github.com/snapcore/spread
.. _general notes: https://github.com/snapcore/snapcraft/blob/main/TESTING.md#spread-tests-for-the-snapcraft-snap
