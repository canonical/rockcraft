.. meta::
    :description: How to install a custom Chisel package slice into a Rockcraft project when the slice definition is not yet available in upstream Chisel releases.

.. _how-to-install-a-custom-package-slice:

Install a custom package slice
==============================

When a specific package slice is not available on the `upstream Chisel
releases <https://github.com/canonical/chisel-releases>`_, you will more
likely end up creating your own slice definition.

Once you have it though, the most obvious question is: **how can I install
this custom slice with Chisel?**

Let's assume you want to install the ``vim-tiny`` slice created following the
:ref:`Chisel documentation <chisel:slice_package>`. This guide can be
applied to other packages by following this guide
and replacing any mention of ``vim-tiny`` with your desired sliced program.

Chisel will only recognise slices belonging to a Chisel release, so you need
to copy your slice definitions file - ``vim-tiny.yaml`` - into
the ``chisel-releases/slices`` folder in your ``chisel-releases`` clone.
Note that if a slice definitions file
with the same name already exists, it most likely means that the package
you're slicing has already been sliced before, and in this case, you only
need to merge your changes into that existing file.

After this, you should be able to find your custom  slice ``bins``
in the local Chisel release:

.. code-block:: bash

   chisel find --release=./chisel-releases/ vim-tiny_bins

If you wanted to test it with Chisel alone, you could now simply run

.. code-block:: bash

   # Testing with Chisel directly:
   mkdir -p my-custom-vim-tiny-fs
   chisel cut --release ./chisel-releases --root my-custom-vim-tiny-fs vim-tiny_bins

You should end up with a folder named "my-custom-vim-tiny-fs" containing a few
folders, amongst which there would be ``./usr/bin/vim-tiny``.

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

The "build-context" part allows you to send the local ``chisel-releases``
folder into the builder. The "override-build" enables you to install your
custom slice.
Please note that this level of customisation is only needed when you want to
install from a custom Chisel release. If the desired slice definitions are
already upstream, then you can simply use ``stage-packages``, as demonstrated
in :ref:`here <how-to-chisel-a-rock>`.

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

And that's it! You've now built your own rock from a custom Chisel release.

Next step: share your slice definitions file with others!
It is as simple as proposing your changes into the upstream
`Chisel releases repository <https://github.com/canonical/chisel-releases>`_.
