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

