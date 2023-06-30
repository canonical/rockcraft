How to install your own package slice
*************************************

When a specific package slice is not available on the `upstream Chisel
releases <https://github.com/canonical/chisel-releases>`_, you will more
likely end up creating your own slice definition.

Once you have it though, the most obvious question is: **how can I install
this custom slice with Chisel?**

Let's assume you want to install the OpenSSL binaries slice created in
:doc:`this guide <create-slice>`.

**First**, clone the Chisel releases repository:

.. literalinclude:: code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:clone-chisel-releases]
    :end-before: [docs:clone-chisel-releases-end]
    :dedent: 2

This repository acts as the database of slice definitions files for each
Chisel release (Chisel releases are named analogously to Ubuntu releases, and
mapped into Git branches within the repository).

Chisel will only recognise slices belonging to a Chisel release, so you need
to copy your slice definitions file - ``openssl.yaml`` in this example - into
the ``chisel-releases/slices`` folder. Note that if a slice definitions file
with the same name already exists, it most likely means that the package
you're slicing has already been sliced before, and in this case, you only
need to merge your changes into that existing file.

At this point, you should be able to find your custom OpenSSL slice ``bins``
in the local Chisel release:

.. literalinclude:: code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:slice-exists]
    :end-before: [docs:slice-exists-end]
    :dedent: 2

If you wanted to test it with Chisel alone, you could now simply run

.. literalinclude:: code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:cut]
    :end-before: [docs:cut-end]
    :dedent: 2

You should end up with a folder named "my-custom-openssl-fs" containing a few
folders, amongst which there would be ``./usr/bin/openssl``.

**To install the custom package slice into a ROCK though**, you need to use
Rockcraft!

Start by initialising a new Rockcraft project:

.. literalinclude:: code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:init]
    :end-before: [docs:init-end]
    :dedent: 2

After this command, you should find a new ``rockcraft.yaml`` file in your
current path.

Adjust the ``rockcraft.yaml`` file according to the following content (feel
free to adjust the metadata, but pay special attention to the ``parts``
section):

.. literalinclude:: code/install-slice/rockcraft.yaml
    :language: yaml

The "build-context" part allows you to send the local ``chisel-releases``
folder into the builder. The "override-build" enables you to install your
custom slice.
Please not that this level of customisation is only needed when you want to
install from a custom Chisel release. If the desired slice definitions are
already upstream, then you can simply use ``stage-packages``, as demonstrated
in :ref:`here <chisel-example>`.

Build your ROCK with:

.. literalinclude:: code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:pack]
    :end-before: [docs:pack-end]
    :dedent: 2

The output will be:

..  code-block:: text
    :emphasize-lines: 4,6,8,10,12,17
    :class: log-snippets

    Launching instance...
    Retrieved base bare for amd64
    Extracted bare:latest
    Executed: pull build-context
    Executed: pull pebble
    Executed: overlay build-context
    Executed: overlay pebble
    Executed: build build-context
    Executed: build pebble
    Executed: stage build-context
    Executed: stage pebble
    Executed: prime build-context
    Executed: prime pebble
    Executed parts lifecycle
    Created new layer
    Labels and annotations set to ['org.opencontainers.image.version=0.0.1', 'org.opencontainers.image.title=custom-openssl-rock', 'org.opencontainers.image.ref.name=custom-openssl-rock', 'org.opencontainers.image.licenses=GPL-3.0', 'org.opencontainers.image.created=2022-11-25T14:00:47.470814+00:00', 'org.opencontainers.image.base.digest=c4d1cae85485fb5bf8483a440f7e47b0fd2592ff114117cd4763604fbf6ae7a4']
    Exported to OCI archive 'custom-openssl-rock_0.0.1_amd64.rock'

Test that the OpenSSL binaries have been correctly installed with the following:

.. literalinclude:: code/install-slice/task.yaml
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

.. literalinclude:: code/install-slice/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

The output of the Docker command will be OpenSSL's default help message:

..  code-block:: text
    :class: log-snippets

    help:

    Standard commands
    asn1parse         ca                ciphers           cmp
    cms               crl               crl2pkcs7         dgst
    dhparam           dsa               dsaparam          ec
    ecparam           enc               engine            errstr
    fipsinstall       gendsa            genpkey           genrsa
    help              info              kdf               list
    mac               nseq              ocsp              passwd
    pkcs12            pkcs7             pkcs8             pkey
    pkeyparam         pkeyutl           prime             rand
    rehash            req               rsa               rsautl
    s_client          s_server          s_time            sess_id
    <... many more lines of output>


And that's it! You've now built your own ROCK from a custom Chisel release.
Next step: share your slice definitions file with others!
