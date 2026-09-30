.. meta::
    :description: How to migrate an existing Docker image to a chiselled Rockcraft rock. Step-by-step guide using Skopeo and LXD to build a minimal, secure OCI container image.

.. _how-to-migrate-a-docker-image-to-a-chiselled-rock:

Migrate a Docker image to a chiseled rock
==========================================

Prerequisites
-------------
- snap enabled system (https://snapcraft.io)
- LXD installed (https://documentation.ubuntu.com/lxd/)
- skopeo installed (https://github.com/containers/skopeo).
  Skopeo will also be automatically installed as a Rockcraft dependency
- Docker installed (https://snapcraft.io/docker)
- a text editor


Install Rockcraft
-----------------

Install Rockcraft on your host:

.. literalinclude:: ../../tutorial/code/hello-world/task.yaml
    :language: bash
    :start-after: [docs:install-rockcraft]
    :end-before: [docs:install-rockcraft-end]
    :dedent: 2

Project Setup
-------------

For this tutorial, the reference Docker image will be
`Microsoft's .NET Runtime 10.0`_. The target base Ubuntu release will be Resolute (26.04), and the
target architecture will be ``amd64``.

Create a new directory, write the reference Dockerfile (pasted below) into a
text editor and save it as ``Dockerfile``:

.. literalinclude:: ../code/migrate-to-chiselled-rock/Dockerfile
    :language: Docker

For the sake of comparison, start by building this Docker image by running:


.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:build-docker-image]
    :end-before: [docs:build-docker-image-end]
    :dedent: 2

The output should be similar to:

..  code-block:: text
    :emphasize-lines: 15
    :class: log-snippets

    [+] Building 37.1s (10/10) FINISHED                                 docker:default
    => [internal] load build definition from Dockerfile                          0.0s
    => => transferring dockerfile: 1.12kB                                        0.0s
    => [internal] load metadata for mcr.microsoft.com/dotnet/runtime-deps:10.0.  0.7s
    => [internal] load metadata for docker.io/amd64/buildpack-deps:resolute-cur  1.7s
    => [internal] load .dockerignore                                             0.0s
    => => extracting sha256:2c7ba87ef970733d62efe74fdb09e39f78f3970903f21372e09  1.2s
    => => extracting sha256:68a0c2f8197c261d8dc63644fa58de90d1bdaa782cf866f0e5b  0.0s
    => [installer 2/2] RUN dotnet_version=10.0.8     && curl --fail --show-err  16.1s
    => [stage-1 2/3] COPY --from=installer [/dotnet, /usr/share/dotnet]          0.2s
    => [stage-1 3/3] RUN ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet          0.4s
    => exporting to image                                                        2.7s
    => => exporting layers                                                       2.2s
    => => exporting manifest sha256:f5f3158908ec561ef510155e56fc8e064026d56a662  0.0s
    => => naming to docker.io/library/dotnet-runtime:reference                   0.0s
    => => unpacking to docker.io/library/dotnet-runtime:reference                0.5s


Now, inspect this .NET reference image's size:

.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:inspect-docker-image]
    :end-before: [docs:inspect-docker-image-end]
    :dedent: 2

The output should be similar to:

..  code-block:: text
    :emphasize-lines: 2
    :class: log-snippets

    IMAGE                      ID             DISK USAGE   CONTENT SIZE   EXTRA
    dotnet-runtime:reference   70fd872341ed        343MB           96MB

And make sure it is functional:

.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:run-docker-image]
    :end-before: [docs:run-docker-image-end]
    :dedent: 2

The output should look as follows:

..  code-block:: text
    :emphasize-lines: 11
    :class: log-snippets

    Host:
        Version:      10.0.8
        Architecture: x64
        Commit:       94ea82652c
        RID:          linux-x64

    .NET SDKs installed:
        No SDKs were found.

    .NET runtimes installed:
        Microsoft.NETCore.App 10.0.8 [/usr/share/dotnet/shared/Microsoft.NETCore.App]

    Other architectures found:
        None

    Environment variables:
        DOTNET_RUNNING_IN_CONTAINER              [true]
        DOTNET_VERSION                           [10.0.8]

    global.json file:
        Not found

    Learn more:
        https://aka.ms/dotnet/info

    Download .NET:
        https://aka.ms/dotnet/download

Convert Dockerfile to ``rockcraft.yaml`` file
---------------------------------------------

From a quick analysis of the reference Dockerfile above, the following
requirements must be met:

- R1. The rock must be based on Ubuntu Resolute (26.04)
- R2. There is no predefined Entrypoint or default command
- R3. The rock must have version 10.0 of the .NET Runtime installed
- R4. ``/usr/bin/dotnet`` must be a symbolic link to the .NET binary

With these requirements in mind, and in the same directory as the Dockerfile
from above, write the following into a text editor and save it as
``rockcraft.yaml``:

.. literalinclude:: ../code/migrate-to-chiselled-rock/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

Note the subtle chiselling of the .NET Runtime package in ``rockcraft.yaml``.
You are requesting Rockcraft to install the ``standard`` slice of the
``dotnet-runtime-10.0`` deb, which is defined in the
`ubuntu-26.04 Chisel release
<https://github.com/canonical/chisel-releases/tree/ubuntu-26.04/slices/>`_.


Pack the Chiselled Rock with Rockcraft
--------------------------------------

To build the rock, run:

.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:build-rock]
    :end-before: [docs:build-rock-end]
    :dedent: 2

The output should be similar to:

..  code-block:: text
    :class: log-snippets

    2026-05-26 16:44:26.830 Starting rockcraft, version 1.19.0
    ...
    2026-05-26 16:44:27.329 Launching managed ubuntu 26.04 instance...
    2026-05-26 16:44:27.329 Executing on host: lxc remote list --format=yaml
    ...
    2026-05-26 16:45:29.562 Building install-dotnet-runtime
    2026-05-26 16:45:29.564 execute action install-dotnet-runtime:Action(part_name='install-dotnet-runtime', step=Step.BUILD, action_type=ActionType.RUN, reason=None, project_vars=ProjectVarInfo(root={}), properties=ActionProperties(changed_files=None, changed_dirs=None))
    2026-05-26 16:45:29.566 load state file: /root/parts/install-dotnet-runtime/state/pull
    2026-05-26 16:45:29.788 :: 2026/05/26 16:45:29 Consulting release repository...
    2026-05-26 16:45:30.309 :: 2026/05/26 16:45:30 Fetching current ubuntu-26.04 release...
    2026-05-26 16:45:30.524 :: 2026/05/26 16:45:30 Processing ubuntu-26.04 release...
    2026-05-26 16:45:40.419 :: 2026/05/26 16:45:40 Selecting slices...
    2026-05-26 16:45:40.420 :: 2026/05/26 16:45:40 Fetching ubuntu 26.04 resolute suite details...
    2026-05-26 16:45:40.673 :: 2026/05/26 16:45:40 Release date: Thu, 23 Apr 2026 17:07:15 UTC
    2026-05-26 16:45:40.675 :: 2026/05/26 16:45:40 Fetching index for ubuntu 26.04 resolute main component...
    2026-05-26 16:45:41.440 :: 2026/05/26 16:45:41 Fetching index for ubuntu 26.04 resolute universe component...
    2026-05-26 16:45:49.441 :: 2026/05/26 16:45:49 Fetching ubuntu 26.04 resolute-security suite details...
    2026-05-26 16:45:49.619 :: 2026/05/26 16:45:49 Release date: Tue, 26 May 2026 12:45:13 UTC
    2026-05-26 16:45:49.621 :: 2026/05/26 16:45:49 Fetching index for ubuntu 26.04 resolute-security main component...
    2026-05-26 16:45:49.703 :: 2026/05/26 16:45:49 Fetching index for ubuntu 26.04 resolute-security universe component...
    2026-05-26 16:45:49.762 :: 2026/05/26 16:45:49 Fetching ubuntu 26.04 resolute-updates suite details...
    2026-05-26 16:45:49.935 :: 2026/05/26 16:45:49 Release date: Tue, 26 May 2026 12:45:19 UTC
    2026-05-26 16:45:49.936 :: 2026/05/26 16:45:49 Fetching index for ubuntu 26.04 resolute-updates main component...
    2026-05-26 16:45:50.013 :: 2026/05/26 16:45:50 Fetching index for ubuntu 26.04 resolute-updates universe component...
    2026-05-26 16:45:50.083 :: 2026/05/26 16:45:50 Fetching pool/main/b/base-files/base-files_14ubuntu6.1_amd64.deb...
    2026-05-26 16:45:50.155 :: 2026/05/26 16:45:50 Fetching pool/main/d/dotnet10/dotnet-host-10.0_10.0.8-0ubuntu1~26.04.1_amd64.deb...
    2026-05-26 16:45:50.268 :: 2026/05/26 16:45:50 Fetching pool/main/g/glibc/libc6_2.43-2ubuntu2_amd64.deb...
    2026-05-26 16:45:51.332 :: 2026/05/26 16:45:51 Fetching pool/universe/g/gcc-14/gcc-14-base_14.3.0-14ubuntu1_amd64.deb...
    2026-05-26 16:45:51.386 :: 2026/05/26 16:45:51 Fetching pool/main/g/gcc-16/libgcc-s1_16-20260322-1ubuntu1_amd64.deb...
    2026-05-26 16:45:51.455 :: 2026/05/26 16:45:51 Fetching pool/main/g/gcc-16/libstdc++6_16-20260322-1ubuntu1_amd64.deb...
    2026-05-26 16:45:51.815 :: 2026/05/26 16:45:51 Fetching pool/main/d/dotnet10/dotnet-hostfxr-10.0_10.0.8-0ubuntu1~26.04.1_amd64.deb...
    2026-05-26 16:45:51.909 :: 2026/05/26 16:45:51 Fetching pool/main/d/dotnet10/dotnet-runtime-10.0_10.0.8-0ubuntu1~26.04.1_amd64.deb...
    ...
    2026-05-26 16:46:15.523 Created new layer
    2026-05-26 16:46:15.524 Adding Pebble entrypoint
    2026-05-26 16:46:15.525 Configuring entrypoint...
    2026-05-26 16:46:15.544 Entrypoint set to ['/usr/bin/pebble', 'enter']
    2026-05-26 16:46:15.567 Entrypoint set to ['/bin/pebble', 'enter']
    2026-05-26 16:46:15.571 Adding metadata
    2026-05-26 16:46:15.572 Configuring labels and annotations...
    2026-05-26 16:46:15.592 Labels and annotations set to ['org.opencontainers.image.version=chiselled', 'org.opencontainers.image.title=dotnet-runtime', 'org.opencontainers.image.created=2026-05-26T14:46:15.571853+00:00', 'org.opencontainers.image.description=.NET Runtime 10.0\n\nA Chiselled rock for the .NET Runtime 10.0', 'org.opencontainers.image.licenses=Apache-2.0']
    2026-05-26 16:46:15.593 Setting the rock's control data
    2026-05-26 16:46:15.594 Adding to layer: /tmp/tmpljv_j_q4/.rock as '.rock'
    2026-05-26 16:46:15.595 Adding to layer: /tmp/tmpljv_j_q4/.rock/metadata.yaml as '.rock/metadata.yaml'
    2026-05-26 16:46:15.612 Control data written
    2026-05-26 16:46:15.612 Metadata added
    2026-05-26 16:46:15.613 Exporting to OCI archive
    2026-05-26 16:46:15.816 Exported to OCI archive 'dotnet-runtime_chiselled_amd64.rock'

At the end of the process, a file named ``dotnet-runtime_chiselled_amd64.rock``
should be present in the current directory. That's your chiseled rock,
as an OCI archive.


Test the rock
-------------

First, import the recently created rock into Docker:

.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Now inspect the chiseled .NET Runtime rock the same way as it was done for the
reference Docker image:

.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:inspect-rock]
    :end-before: [docs:inspect-rock-end]
    :dedent: 2

Which should print something like:

..  code-block:: text
    :emphasize-lines: 2
    :class: log-snippets

    IMAGE                      ID             DISK USAGE   CONTENT SIZE   EXTRA
    dotnet-runtime:chiselled   a846a767e8e8        213MB         64.5MB

And make sure this rock is as functional as the reference Docker image:

.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:run-rock]
    :end-before: [docs:run-rock-end]
    :dedent: 2

The output should be similar to:

..  code-block:: text
    :emphasize-lines: 11
    :class: log-snippets

    Host:
        Version:      10.0.8
        Architecture: x64
        Commit:       94ea82652c
        RID:          ubuntu.26.04-x64

    .NET SDKs installed:
        No SDKs were found.

    .NET runtimes installed:
        Microsoft.NETCore.App 10.0.8 [/usr/lib/dotnet/shared/Microsoft.NETCore.App]

    Other architectures found:
        None

    Environment variables:
        Not set

    global.json file:
        Not found

    Learn more:
        https://aka.ms/dotnet/info

    Download .NET:
        https://aka.ms/dotnet/download

Conclusion
----------

In this tutorial, you have migrated from an imperative container build
instructions (Dockerfile) to a declarative one (``rockcraft.yaml``), without any
overhead on the final file's size or complexity.

The resulting rock ended up being 31.5MB smaller than the reference one, while
offering the same .NET Runtime functionality.

.. _Microsoft's .NET Runtime 10.0: https://github.com/dotnet/dotnet-docker/tree/main/src/runtime/10.0/resolute
