.. _how-to:

How-to guides
=============

These guides accompany you through crafting, chiselling, and publishing rocks with
Rockcraft.


Crafting
--------

The starting point of a rock is a Rockcraft project, which defines what goes into the
rock and what machinery builds it. Once a project is complete, the rock can be packed
either locally or remotely, and then published to an image registry.

- :ref:`how-to-migrate-a-docker-image-to-a-chiselled-rock`
- :ref:`how-to-publish-a-rock-to-a-registry`


Chiselling
----------

Containers often contain redundant or unneeded software in their baseline systems.
Chisel cuts software collections into manageable slices that can layered within rocks to
make them leaner.

- :ref:`how-to-chisel-a-rock`
- :ref:`how-to-create-a-package-slice-for-chisel`


12-factor web app rocks
-----------------------

Rocks are especially suitable as containers for 12-factor apps and their components.

- :ref:`how-to-manage-a-12-factor-app-rock`


Documentation
-------------

The Rockcraft documentation is always evolving. We welcome people of all skill levels to
contribute to it.

- :ref:`how-to-contribute-to-rockcraft-documentation`
- :ref:`how-to-build-the-documentation`

.. toctree::
    :hidden:
    :maxdepth: 1

    get-started
    crafting/index
    chiselling/index
    Rocks for 12-factor apps <web-app-rocks/index>
    documentation/index
