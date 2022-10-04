*********
Tutorials
*********


Create a Hello World ROCK
=========================

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

.. code-block:: sh

    $ snap install rockcraft --classic --edge

Project Setup
-------------

Create a new directory and write following into a text editor and
save it as ``rockcraft.yaml``:

.. code-block:: yaml

    name: hello
    summary: Hello World
    description: The most basic example of a ROCK.
    version: "1.0"
    base: ubuntu:20.04
    license: Apache-2.0
    cmd: [/usr/bin/hello, -t]
    platforms:
      amd64:  # Make sure this value matches your computer's architecture

    parts:
      hello:
        plugin: nil
        overlay-packages:
          - hello

Pack the ROCK with Rockcraft
----------------------------

To build the ROCK, run:

.. code-block:: sh

    $ rockcraft pack


The output should look as follows:

.. code-block:: sh

    Launching instance...
    Retrieved base ubuntu:20.04
    Extracted ubuntu:20.04
    Executed: pull hello
    Executed: overlay hello
    Executed: build hello
    Executed: stage hello
    Executed: prime hello
    Executed parts lifecycle
    Created new layer
    Cmd set to ['/usr/bin/hello', '-t']
    Labels and annotations set to ['org.opencontainers.image.version=1.0', 'org.opencontainers.image.title=hello', 'org.opencontainers.image.ref.name=hello', 'org.opencontainers.image.licenses=Apache-2.0', 'org.opencontainers.image.created=2022-06-30T09:07:38.124741+00:00']
    Exported to OCI archive 'hello_1.0_amd64.rock'

At the end of the process, a file named ``hello_1.0_amd64.rock`` should be
present in the current directory. That's your ROCK, in oci-archive format.


Run the ROCK in Docker
----------------------

First, import the recently created ROCK into Docker:

.. code-block:: sh

    skopeo --insecure-policy copy oci-archive:hello_1.0_amd64.rock docker-daemon:hello:1.0

Now run the ``hello`` command from the ROCK:

.. code-block:: sh

    $ docker run hello:1.0

Which should print:

.. code-block:: sh

    hello, world


Install packages slices into a ROCK
===================================

In this tutorial, you will create a lean ROCK that contains a fully functional OpenSSL installation, and you will verify
that it is functional by loading the ROCK into Docker and using it to validate the certificates of the Ubuntu website.

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

.. code-block:: sh

    snap install rockcraft --classic --edge


Project Setup
-------------

Create a new directory, write the following into a text editor and save it as ``rockcraft.yaml``:

.. code-block:: yaml

    name: chisel-openssl
    summary: OpenSSL from Chisel slices
    description: A "bare" ROCK containing an OpenSSL installation created from Chisel slices.
    license: Apache-2.0

    version: "0.0.1"
    base: bare
    build_base: "ubuntu:22.04"
    entrypoint: [/usr/bin/openssl]
    platforms:
      amd64:

    env:
      - SSL_CERT_FILE: /etc/ssl/certs/ca-certificates.crt

    parts:
      openssl:
        plugin: nil
        stage-packages:
          - openssl_bins
          - ca-certificates_data

Note that this Rockcraft file uses the ``openssl_bins`` and ``ca-certificates_data`` Chisel slices to generate an image
containing only files that are strictly necessary for a functional OpenSSL installation. See :ref:`what-is-chisel` for
details on the Chisel tool.


Pack the ROCK with Rockcraft
----------------------------

To build the ROCK, run:

.. code-block:: sh

    rockcraft

The output will look similar to:

.. code-block:: sh

    Launching instance...
    Retrieved base bare for amd64
    Extracted bare:latest
    Executed: pull openssl
    Executed: overlay openssl
    Executed: build openssl
    Executed: stage openssl
    Executed: prime openssl
    Executed parts lifecycle
    Created new layer
    Entrypoint set to ['/usr/bin/openssl']
    Cmd set to []
    Environment set to ['SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt']
    Labels and annotations set to ['org.opencontainers.image.version=0.0.1', 'org.opencontainers.image.title=chisel-openssl', 'org.opencontainers.image.ref.name=chisel-openssl', 'org.opencontainers.image.licenses=Apache-2.0', 'org.opencontainers.image.created=2022-09-30T17:57:57.070040+00:00', 'org.opencontainers.image.base.digest=719e29cbdf81d2c046598c274ae82bdcdfe7bf819058a0f304c57858b633d801']
    Exported to OCI archive 'chisel-openssl_0.0.1_amd64.rock'

The process might take a little while, but at the end, a new file named ``chisel-openssl_0.0.1_amd64.rock`` will be
present in the current directory. That's your OpenSSL ROCK, in oci-archive format.

Run the ROCK in Docker
----------------------

First, import the recently created ROCK into Docker:

.. code-block:: sh

    skopeo --insecure-policy copy oci-archive:chisel-openssl_0.0.1_amd64.rock docker-daemon:chisel-openssl:latest

Now you can run a container from the ROCK:

.. code-block:: sh

    docker run chisel-openssl

The output will be OpenSSL's default help message, which starts like this:

.. code-block:: sh

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

As you can see, OpenSSL has many features. Use one of them to check that Ubuntu's website has valid SSL certificates:

.. code-block:: sh

    docker run --rm chisel-openssl s_client -connect ubuntu.com:443 -brief

The output will look similar to the following:

.. code-block:: sh

    CONNECTION ESTABLISHED
    Protocol version: TLSv1.3
    Ciphersuite: TLS_AES_256_GCM_SHA384
    Peer certificate: CN = ubuntu.com
    Hash used: SHA256
    Signature type: RSA-PSS
    Verification: OK
    Server Temp Key: X25519, 253 bits

The ``Verification: OK`` line indicates that the OpenSSL installation inside your ROCK was able to validate Ubuntu
Website's certificates successfully.


Publish a ROCK to a registry
============================

Prerequisites
-------------

- skopeo installed (https://github.com/containers/skopeo)
- Docker installed (https://docs.docker.com/get-docker/)


Push a ROCK to Docker Hub
-------------------------

The output of ``rockcraft pack`` is a ROCK in its oci-archive archive format. For the sake of this tutorial,
let's say that this file's name is "myrock_1.0_amd64.rock", and that you want to push it to Docker Hub,
as "tutorials/myrock:1.0":

.. code-block:: sh

    $ skopeo --insecure-policy copy --multi-arch all oci-archive:myrock_1.0_amd64.rock docker://tutorials/myrock:1.0
    Getting image source signatures
    Copying blob e65b2e587073 skipped: already exists
    Copying blob 01f981dde5a5 skipped: already exists
    Copying config 5da22a9016 done
    Writing manifest to image destination
    Storing signatures

