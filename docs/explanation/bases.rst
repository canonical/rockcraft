.. _bases_explanation:

Bases
=====

One mandatory field for every rock project is the
:ref:`base <rockcraft_yaml_base>`.

This field defines the baseline system upon which the rock's contents shall be
layered on. Only Ubuntu and ``bare``
:ref:`bases <rockcraft_yaml_base>` are supported.

Ubuntu bases
------------

When setting an Ubuntu
:ref:`base <rockcraft_yaml_base>` for a rock, Rockcraft will pull the
corresponding Ubuntu base container image from a container registry. This is
exactly the same container one would get from places like
`Docker Hub <docker_hub_>`_ or `Amazon ECR <ecr_>`_.

The resulting rock will therefore also contain any software and utilities that
are present in the Ubuntu base container images.

Setting an Ubuntu :ref:`base <rockcraft_yaml_base>` for a rock is
especially useful when the goal is to build a rock that can be used for
general-purpose environments such as a development working space.

Bare bases
----------

As the name suggests, a ``bare`` :ref:`base <rockcraft_yaml_base>` indicates
that the rock shall have no
baseline system. This definition is similar to the "`scratch`_" Docker image,
with the exception that a rock **can never be completely empty**, as it must
always include a minimum baseline with :ref:`pebble_explanation_page`
and additional metadata (:ref:`what-sets-rocks-apart`).

When and how to use a ``bare`` base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``bare`` :ref:`base <rockcraft_yaml_base>` is extremely useful when
the goal is to build a lean **chiselled rock**. Such rocks are typically
preferred for production environments due to their optimised deployment
efficiency and reduced attack surface. The combination of the
``bare`` :ref:`base <rockcraft_yaml_base>`
with :ref:`Chisel <chisel_explanation>` slices will result in a minimalist
container image that meets the production environment's criteria while
retaining its functionality.

Note that, when using the ``bare``
:ref:`base <rockcraft_yaml_base>`, the rock will still be
**Ubuntu-based**! As such, Rockcraft needs to know the Ubuntu release to be used
as the :ref:`build environment <rockcraft_yaml_build_base>` for the rock.

For example, if the goal is to have a tiny chiselled rock with software
components coming from the Ubuntu 24.04 release, then the *rockcraft.yaml*
file must have ``base: bare`` and ``build-base: ubuntu@24.04``.

The guide ":ref:`chisel_existing_rock`" provides a practical example on how to
start from a rock with an Ubuntu :ref:`base <rockcraft_yaml_base>` and
apply the changes necessary to build a chiselled rock with a ``bare``
:ref:`base <rockcraft_yaml_base>`.


.. _`ecr`: https://gallery.ecr.aws/ubuntu/ubuntu
.. _`docker_hub`: https://hub.docker.com/_/ubuntu/
.. _`scratch`: https://hub.docker.com/_/scratch
