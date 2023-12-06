Install slices in a ROCK
========================

In this tutorial, you will create a lean ROCK that contains a fully functional
OpenSSL installation, and you will verify that it is functional by loading the
ROCK into Docker and using it to validate the certificates of the Ubuntu
website.

Prerequisites
-------------

- snap enabled system (https://snapcraft.io)
- LXD installed (https://linuxcontainers.org/lxd/getting-started-cli/)
- skopeo installed (https://github.com/containers/skopeo)
- Docker installed (https://docs.docker.com/get-docker/)
- a text editor


Install Rockcraft
-----------------

Install Rockcraft on your host:

.. literalinclude:: code/chisel/task.yaml
    :language: bash
    :start-after: [docs:install-rockcraft]
    :end-before: [docs:install-rockcraft-end]
    :dedent: 2


Project Setup
-------------

Create a new directory, write the following into a text editor and save it as
``rockcraft.yaml``:

.. _chisel-example:

.. literalinclude:: code/chisel/rockcraft.yaml
    :language: yaml

Note that this Rockcraft file uses the ``openssl_bins`` and
``ca-certificates_data`` Chisel slices to generate an image containing only
files that are strictly necessary for a functional OpenSSL installation. See
:ref:`chisel_explanation` for details on the Chisel tool.


Pack the ROCK with Rockcraft
----------------------------

To build the ROCK, run:

.. literalinclude:: code/chisel/task.yaml
    :language: bash
    :start-after: [docs:build-rock]
    :end-before: [docs:build-rock-end]
    :dedent: 2

The output will look similar to:

..  code-block:: text
    :emphasize-lines: 10
    :class: log-snippets

    Launching instance...
    Retrieved base bare for amd64
    Extracted bare:latest
    Executed: pull openssl
    Executed: overlay openssl
    Executed: build openssl
    Executed: stage openssl
    Executed: prime openssl
    Executed parts lifecycle
    Exported to OCI archive 'chisel-openssl_0.0.1_amd64.rock'

The process might take a little while, but at the end, a new file named
``chisel-openssl_0.0.1_amd64.rock`` will be present in the current directory.
That's your OpenSSL ROCK, in oci-archive format.

Run the ROCK in Docker
----------------------

First, import the recently created ROCK into Docker:

.. literalinclude:: code/chisel/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Now you can run a container from the ROCK:

.. literalinclude:: code/chisel/task.yaml
    :language: bash
    :start-after: [docs:docker-run]
    :end-before: [docs:docker-run-end]
    :dedent: 2

The output will be OpenSSL's default help message, which starts like this:

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

As you can see, OpenSSL has many features. Use one of them to check that
Ubuntu's website has valid SSL certificates:

.. literalinclude:: code/chisel/task.yaml
    :language: bash
    :start-after: [docs:docker-run-with-args]
    :end-before: [docs:docker-run-with-args-end]
    :dedent: 2

The output will look similar to the following:

..  code-block:: text
    :class: log-snippets

    CONNECTION ESTABLISHED
    Protocol version: TLSv1.3
    Ciphersuite: TLS_AES_256_GCM_SHA384
    Peer certificate: CN = ubuntu.com
    Hash used: SHA256
    Signature type: RSA-PSS
    Verification: OK
    Server Temp Key: X25519, 253 bits

The ``Verification: OK`` line indicates that the OpenSSL installation inside
your ROCK was able to validate Ubuntu Website's certificates successfully.
