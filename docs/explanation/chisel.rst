.. _chisel_explanation:

Chisel
======

Chisel_ is a software tool for extracting the contents of Debian packages
for use in container images.

    *“The sculpture is already complete within the marble block, before I start
    my work. It is already there, I just have to chisel away the superfluous
    material.”*
    \- Michelangelo

Using the analogy of a tool to carve and cut stone, Chisel is used by
Rockcraft to sculpt minimal container images that only include what is
needed from the Debian packages that are used.

See :ref:`how_to_use_chisel` for information about using the tool.

Package slices
--------------

Since Debian packages are simply archives that can be inspected, navigated
and deconstructed, it is possible to extract slices of packages that contain
minimal, complementary, loosely-coupled sets of files based on package
metadata and content. Such **package slices** are subsets of Debian packages,
with their own content and set of dependencies to other internal and external
slices.

The use of package slices provides Rockcraft with the ability to build minimal
container images from the wider set of Ubuntu packages.

.. figure:: /_static/package-slices.svg
   :width: 75%
   :align: center
   :alt: Debian package slices with dependencies

This image illustrates the simple case where, at a package level, package *B*
depends on package *A*. However, there might be files in *A* that *B* doesn't
actually need, but which are provided for convenience or completeness.
In this example, the files in the package slice, *A_slice3*, are not needed
for *B* to function properly. By cutting packages *A* and *B* into slices, we
can identify the files in *A* that are actually needed by *B*.

With this slice definition in place, Chisel is able to extract a
highly-customized and specialized slice of the Ubuntu distribution, which one
could see as a block of stone from which we can carve and extract only the
small and relevant parts that we need to run our applications. It is ideal to
support the creation of container images that are smaller than those constructed
using full Debian packages, but which are equally functional.

.. _Chisel: https://github.com/canonical/chisel
