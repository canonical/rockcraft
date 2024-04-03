Publish a rock to a registry
============================

Prerequisites
-------------

- skopeo installed (https://github.com/containers/skopeo)
- Docker installed (https://docs.docker.com/get-docker/)


Push a rock to Docker Hub
-------------------------

The output of ``rockcraft pack`` is a rock in its oci-archive archive format.

..  code-block:: bash

    skopeo --insecure-policy copy oci-archive:<your_rock_file.rock> docker://<container_registry>/<repo>:<tag>

Output:

..  code-block:: text
    :class: log-snippets

    Getting image source signatures
    Copying blob e65b2e587073 skipped: already exists
    Copying blob 01f981dde5a5 skipped: already exists
    Copying config 5da22a9016 done
    Writing manifest to image destination
    Storing signatures
