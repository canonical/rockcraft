.. meta::
    :description: How to install a custom Chisel package slice into a rock using a local repository clone.

.. _how-to-install-a-custom-package-slice:

Install a custom package slice
==============================

When a specific package slice is not available on the `upstream Chisel
releases <https://github.com/canonical/chisel-releases>`_, you will more
likely end up creating your own slice definition.

Once you have it though, the most obvious question is: **how can I install
this custom slice with Chisel?**

Let's assume you want to install the <package> slice. Follow this guide
and replace any mention of <package> with your desired sliced program.

First, clone the Chisel releases repository:

.. literalinclude:: ../code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:clone-chisel-releases]
    :end-before: [docs:clone-chisel-releases-end]
    :dedent: 2

This repository acts as the database of slice definitions files for each
Chisel release. Chisel releases are named analogously to Ubuntu releases, and
mapped into Git branches within the repository.

Chisel will only recognise slices belonging to a Chisel release, so you need
to copy your slice definitions file - ``<package>.yaml`` - into
the ``chisel-releases/slices`` folder. Note that if a slice definitions file
with the same name already exists, it most likely means that the package
you're slicing has already been sliced before, and in this case, you only
need to merge your changes into that existing file.

After this, you should be able to find your custom  slice ``bins``
in the local Chisel release:

.. literalinclude:: ../code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:slice-exists]
    :end-before: [docs:slice-exists-end]
    :dedent: 2

If you wanted to test it with Chisel alone, you could now simply run

.. literalinclude:: ../code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:cut]
    :end-before: [docs:cut-end]
    :dedent: 2

You should end up with a folder named "my-custom-<package>-fs" containing a few
folders, amongst which there would be ``./usr/bin/<package>``.

To install the custom package slice into a rock, you need to use
Rockcraft.

Start by initialising a new Rockcraft project:

.. literalinclude:: ../code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:init]
    :end-before: [docs:init-end]
    :dedent: 2

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
in :ref:`here <chisel-example>`. CHECK THIS LINK

Build your rock with:

.. literalinclude:: ../code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

Test that the <package> binaries have been correctly installed with the following:

.. literalinclude:: ../code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

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

.. literalinclude:: ../code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

And that's it! You've now built your own rock from a custom Chisel release.

Next step: share your slice definitions file with others!
It is as simple as proposing your changes into the upstream
`Chisel releases repository <https://github.com/canonical/chisel-releases>`_.
