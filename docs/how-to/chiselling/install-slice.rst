.. meta::
    :description: How to install a custom Chisel package slice into a Rockcraft project when the slice definition is not yet available in upstream Chisel releases.

.. _how-to-install-a-custom-package-slice:

Install a custom package slice
==============================

When a sliced package isn't available in the `Chisel releases
<https://github.com/canonical/chisel-releases>`__, you will need to create it yourself.
Once it's created, you can install it in your rock.

In this guide, we show how to install the vim-tiny slice built in
:external+chisel:ref:`slice_package` from the Chisel documentation. As you're working through it, replace any mention of vim-tiny with your slice.

Chisel will only recognize slices belonging to a Chisel release, so you need to copy
your slice definitions file -- ``vim-tiny.yaml`` -- into the ``chisel-releases/slices/``
folder in your clone of the chisel-releases repository. Note that if a slice definitions
file with the same name already exists, it most likely means that the package you're
slicing has already been sliced before, and in this case, you only need to merge your
changes into that existing file.

After this, you should be able to find your custom  slice ``bins``
in the local Chisel release:

.. code-block:: bash

   chisel find --release=./chisel-releases/ vim-tiny_bins

If you wanted to test it with Chisel alone, you could now simply run

.. code-block:: bash

   # Testing with Chisel directly:
   mkdir -p my-custom-vim-tiny-fs
   chisel cut --release ./chisel-releases --root my-custom-vim-tiny-fs vim-tiny_bins

You should end up with a ``my-custom-vim-tiny-fs/`` directory containing a few
directories, amongst which there would be ``usr/bin/vim-tiny``.

To install the custom package slice into a rock, you need to use
Rockcraft.

Start by initialising a new Rockcraft project:

.. code-block:: bash

   rockcraft init

After this command, you should find a new ``rockcraft.yaml`` file in your
current path.

Adjust the project file according to the following content. Feel
free to adjust the metadata, but pay special attention to the ``parts``
section:

.. literalinclude:: ../code/install-slice/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

The ``build-context`` part allows you to send the local ``chisel-releases`` folder into
the builder. The ``override-build`` key enables you to install your custom slice.

This level of customization is only needed when you want to install from a custom Chisel
release. If the desired slice definitions are already upstream, then you can simply use
the ``stage-packages`` key, as demonstrated in :ref:`how-to-chisel-a-rock`.

Build your rock with:

.. code-block:: bash

   rockcraft pack

Test that the vim-tiny binaries have been correctly installed with the following:

.. code-block:: bash

   sudo rockcraft.skopeo --insecure-policy copy oci-archive:custom-vim-tiny-rock_0.0.1_amd64.rock docker-daemon:chisel-vim-tiny:latest

The output will be:

..  code-block:: text
    :class: log-snippets

    Getting image source signatures
    Copying blob 253d707d7e97 done
    Copying blob 7044a53e1935 done
    Copying config c114b59704 done
    Writing manifest to image destination
    Storing signatures

And after:

.. code-block:: bash

   docker run --rm chisel-vim-tiny exec vim-tiny

And that's it! You've now built your own rock from a custom slice and a custom Chisel
release.
