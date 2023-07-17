.. _how_to_convert_rock_to_docker_image:

Convert your ROCK to a docker image
===================================

Prerequisites
-------------

- skopeo installed (https://github.com/containers/skopeo)
- Docker installed (https://docs.docker.com/get-docker/)


Convert a ROCK to a docker image
--------------------------------

To convert ``<rock_name>.rock`` to a docker image do:

.. code-block:: bash

    skopeo --insecure-policy copy oci-archive:<rock_name>.rock docker-daemon:<rock_name>:latest


Let's break down the command to understand what it's does:

``skopeo`` This refers to the path of the skopeo binary.

``--insecure-policy``: This flag tells skopeo to not run policies checks.

``copy``: This permits to copy container images from one location to another.

``oci-archive:<rock_name>.rock``: This is the source location of the ROCK
image. the ``oci-archive`` specifies that the image is an OCI archive format.

``docker-daemon:<rock_name>:latest``: This is the destination location for the
Docker image. It specifies that the image should be copied to a local Docker
daemon named <rock_name> and tagged latest.

Let's check that our image exist:

.. code-block:: bash

  $ docker images <rock_name>:latest

    REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
    <rock_name>  latest    <IMAGE_ID>   <CREATE_TIME>  <SIZE>
