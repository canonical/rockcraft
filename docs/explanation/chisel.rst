.. _what-is-chisel:

What is Chisel?
===============

As the name says, Chisel is a tool for carving and cutting. But carving and
cutting what? Even though we are talking about ROCKs, it's not like these are
actual solid masses one can physically interact with...

`Chisel <https://github.com/canonical/chisel>`_ is a software tool for carving
and cutting **Debian packages**!

One of the key value propositions of Rockcraft is the ability to build truly
minimal container images while honoring the Ubuntu experience. Well, when having
a closer look at a Debian package, it is easy to understand that this artifact
is purely an archive that can be inspected, navigated and deconstructed. Having
noted this, we've come up with the idea of **Package Slices** - minimal,
complimentary and loosely coupled sets of files, based on the package's metadata
and content. Slices are basically subsets of the Debian packages, with their own
content and set of dependencies to other internal and external slices.

.. image:: /_static/package-slices.png
  :width: 95%
  :align: center
  :alt: Debian package slices with dependencies

-----

.. image:: /_static/slice-of-ubuntu.png
  :width: 95%
  :align: center
  :alt: A slice of Ubuntu

This image depicts a simple case, where both packages *A* and *B* are
deconstructed into multiple slices. At a package level, *B* depends on *A*,
but in reality, there might be files in *A* that *B* doesn't actually need (eg.
*A_slice3* isn't needed for *B* to function properly). With this slice
definition in place, Chisel is able to extract a highly-customized and
specialized Slice of the Ubuntu distribution, which one could see as a block of
stone from which we can carve and extract small and relevant parts we need to
run our applications. It is ideal to support the creation of smaller but equally
functional container images.

    *“The sculpture is already complete within the marble block, before I start
    my work. It is already there, I just have to chisel away the superfluous
    material.”*
    \- Michelangelo

In the end, it's like having a slice of Ubuntu - get *just what you need*. You
can *have your cake and eat it too*!


How to use Chisel?
..................

Chisel has been integrated with Rockcraft in a way that it becomes seamless to
users. Packages and slices can be both installed via the ``stage-packages``
field without any ambiguities because slices follow an underscore-driven naming
convention. For instance, ``openssl`` means the whole OpenSSL package, while
``openssl_bins`` means just the binaries slice of the OpenSSL package. And
that's it. Rockcraft will then take care of the installation and priming of your
content into the ROCK. There's an example :ref:`here <chisel-example>`.

Chisel isn't, however, specific to Rockcraft. It can be used on its own! It
relies on a `database of slices <https://github.com/canonical/chisel-releases>`_
that are indexed per Ubuntu release. So for example, the following command:

.. code-block:: bash

  chisel cut --release ubuntu-22.04 --root myrootfs libgcc-s1_libs libssl3_libs

would look into the Ubuntu Jammy archives, fetch the provided packages and
install only the desired slices into the ``myrootfs`` folder.

To learn more about Chisel and how it works, have a look at
`<https://github.com/canonical/chisel>`_.

Do you need a package slice that doesn't exist yet? Please feel free to propose
your slice definition in `<https://github.com/canonical/chisel-releases>`_.
