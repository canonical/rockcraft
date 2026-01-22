:relatedlinks: https://ubuntu.com/about/release-cycle, [Ubuntu&#32;image&#32;on&#32;Docker&#32;Hub](https://hub.docker.com/_/ubuntu), [Ubuntu&#32;image&#32;on&#32;Amazon&#32;ECR](https://gallery.ecr.aws/ubuntu/ubuntu), [Scratch&#32;image&#32;on&#32;Docker&#32;Hub](https://hub.docker.com/_/scratch)

.. _explanation-bases:

Bases
=====

Every rock is built from a *base*, which defines the baseline system that the rock's
contents are layered on. The systems are Ubuntu releases. An empty, or *bare* base, is
also available for lean images.

The base is declared in the project file by the :ref:`Project.base` key.


Ubuntu bases
------------

When building with an Ubuntu base, Rockcraft pulls the corresponding Ubuntu image from a
container registry. These Ubuntu images are the same as the ones hosted in registries
like Docker Hub or Amazon Elastic Container Registry.

The built rock contains the software and utilities from the Ubuntu image.

Setting an Ubuntu base for a rock is especially useful when the goal is to build a rock
that can serve as a general-purpose environment, such as a development workspace.


.. _explanation-bases-lts-and-interim-bases:

LTS and interim bases
~~~~~~~~~~~~~~~~~~~~~

Ubuntu bases are divided into *LTS* and *interim* bases. An LTS base contains an Ubuntu
LTS release and has a 10-year support window. An interim base contains an interim Ubuntu
release and is supported for nine months.

Interim bases have shorter lifespans and contain upcoming or experimental features. For
rocks, they are most suitable for testing software with short lifecycles. Commonly,
images with these bases are used as test-beds for the software in the Ubuntu release
itself.


.. _explanation-bases-bare-bases:

Bare bases
----------

As the name suggests, a *bare* base results in a rock with no baseline system. This
definition is similar to the scratch Docker image, with the exception that a rock *can
never be completely empty*, as it must always include a :ref:`explanation-pebble`
and some :ref:`additional metadata <what-sets-rocks-apart>`.

The bare base is especially useful when the goal is to build a lean chiselled rock.
Such rocks are typically preferred for production environments due to their optimized
deployment efficiency and reduced attack surface. The combination of the bare base with
:ref:`Chisel <explanation-chisel>` slices will result in a minimalist container image
that meets the production environment's criteria while retaining its functionality.

Even with a bare base, when Rockcraft assembles a rock, it needs Ubuntu as the operating
system for its build environment. The project's :ref:`Project.build_base` key determines
which Ubuntu release is provided for the build environment.

For example, if the goal is to have a tiny chiselled rock with software
components coming from the Ubuntu 24.04 release, then the project file must have
``base: bare`` and ``build-base: ubuntu@24.04``.

:ref:`how-to-chisel-a-rock` provides a practical example on how to start from
a rock with an Ubuntu base and apply the changes necessary to build a chiselled rock
with a bare base.
