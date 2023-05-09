.. _how_to_use_chisel:

How to use Chisel
-----------------

Chisel has been integrated with Rockcraft in a way that it becomes seamless to
users. Packages and slices can be both installed via the ``stage-packages``
field without any ambiguities because slices follow an underscore-driven naming
convention. For instance, ``openssl`` means the whole OpenSSL package, while
``openssl_bins`` means just the binaries slice of the OpenSSL package.
Rockcraft will take care of the installation and priming of your
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