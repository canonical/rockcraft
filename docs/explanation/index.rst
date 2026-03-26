.. _explanation:

Explanation
===========

Explanations provide a wider perspective of Rockcraft. They aid in understanding the
concepts and relationships of Rockcraft as a complete system.


Overview
--------

Rockcraft was created to build secure, stable container images. Read on for a bird's-eye
view of what sets Rockcraft and rocks apart from similar tools.

- :ref:`explanation-why-use-rockcraft`
- :ref:`explanation-rocks`

Rockcraft is commonly used alongside Chisel slices to pack the smallest set of files
needed for a rock to run.

- :ref:`explanation-chisel`

The entrypoint for all rocks is Pebble, a lightweight service manager.

- :ref:`explanation-pebble`


Bases
-----

Bases are a key concept in rocks. They ensure that rocks are stable and compatible
across different machines.

- :ref:`explanation-bases`


Parts
-----

Parts are how software is brought into rocks. When a rock is packed, its parts are
processed in a series of ordered, reproducible steps.

- :ref:`parts`
- :ref:`lifecycle`
- :ref:`explanation-overlay-step`

Files travel as bundles through the parts lifecycle. These bundles are called
*filesets*.

- :ref:`filesets_explanation`


Cryptography
------------

Rockcraft and its external libraries use cryptographic tools for fetching files,
communicating with local processes, and storing user credentials.

- :ref:`Cryptographic technology <explanation-cryptographic-technology>`


.. toctree::
    :hidden:

    Cryptographic technology <cryptography>
    rockcraft
    chisel
    overlay-step
    rocks
    bases
    pebble
    lifecycle-layer
    /common/craft-parts/explanation/filesets
    /common/craft-parts/explanation/parts
    /common/craft-parts/explanation/lifecycle
    /common/craft-parts/explanation/dump_plugin
    usrmerge
