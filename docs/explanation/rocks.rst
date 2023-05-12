.. _rocks_explanation:

ROCKs
=====

ROCKs are container images that are compliant with the `Open Container
Initiative`_ (OCI) `image format specification <OCI_image_spec_>`_.
This means that ROCKs are interoperable with other tools that work with
OCI-compliant images.

A ROCK can be stored in an existing container registry, very much like any
Docker image, and run in the same way as any other container image.
For example, Docker can be used to run a ROCK with the usual command line
syntax:

.. code:: bash

   docker run <rock> ...

Interoperability between ROCKs and other containers also extends to the way
that container images are built. This enables the use of existing build
recipes, such as Dockerfiles, with ROCKs. It also opens up the possibility of
using existing ROCKs as base images for further customisation and development.

.. include:: /links.txt

