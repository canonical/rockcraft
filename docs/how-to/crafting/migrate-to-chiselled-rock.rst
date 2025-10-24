.. _how-to-migrate-a-docker-image-to-a-chiselled-rock:

Migrate a Docker image to a chiselled rock
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
`Microsoft's .NET Runtime 6.0`_. The target base Ubuntu release will be Jammy, and the
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

The output should look as follows:

..  code-block:: text
    :emphasize-lines: 16
    :class: log-snippets

    [+] Building 0.6s (10/10) FINISHED
    => [internal] load .dockerignore0.0s
    => => transferring context: 2B0.0s
    => [internal] load build definition from Dockerfile    0.0s
    => => transferring dockerfile: 881B   0.0s
    => [internal] load metadata for mcr.microsoft.com/dotnet/runtime-deps:6.0.16-jammy-amd64    0.1s
    => [internal] load metadata for docker.io/amd64/buildpack-deps:jammy-curl    0.6s
    => [stage-1 1/3] FROM mcr.microsoft.com/dotnet/runtime-deps:6.0.16-jammy-amd64@sha256:e764c6f0cc866a1f2932  0.0s
    => [installer 1/2] FROM docker.io/amd64/buildpack-deps:jammy-curl@sha256:e1f00c6daf4cd328bbef9c52e6c60f18a  0.0s
    => CACHED [installer 2/2] RUN dotnet_version=6.0.16&& curl -fSL --output dotnet.tar.gz https://dotnet  0.0s
    => CACHED [stage-1 2/3] COPY --from=installer [/dotnet, /usr/share/dotnet]   0.0s
    => CACHED [stage-1 3/3] RUN ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet   0.0s
    => exporting to image   0.0s
    => => exporting layers  0.0s
    => => writing image sha256:a24cab51d4d02019dafcd22a2e2a3e1e6d033f9bbf1cb401d465cb2426bb2264 0.0s
    => => naming to docker.io/library/dotnet-runtime:reference   0.0s

Now, inspect this .NET reference image's size:

.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:inspect-docker-image]
    :end-before: [docs:inspect-docker-image-end]
    :dedent: 2

The output should look as follows:

..  code-block:: text
    :emphasize-lines: 2
    :class: log-snippets

    REPOSITORY TAG IMAGE ID CREATED SIZE
    dotnet-runtime   reference   a24cab51d4d0   4 minutes ago   187MB


And make sure it is functional:

.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:run-docker-image]
    :end-before: [docs:run-docker-image-end]
    :dedent: 2

The output should look as follows:

..  code-block:: text
    :emphasize-lines: 13
    :class: log-snippets

    global.json file:
    Not found

    Host:
    Version:6.0.16
    Architecture: x64
    Commit: 1e620a42e7

    .NET SDKs installed:
    No SDKs were found.

    .NET runtimes installed:
    Microsoft.NETCore.App 6.0.16 [/usr/share/dotnet/shared/Microsoft.NETCore.App]

    Download .NET:
    https://aka.ms/dotnet-download

    Learn about .NET Runtimes and SDKs:
    https://aka.ms/dotnet/runtimes-sdk-info


Convert Dockerfile to ``rockcraft.yaml`` file
---------------------------------------------

From a quick analysis of the reference Dockerfile above, the following
requirements must be met:

- R1. The rock must be based on Ubuntu Jammy
- R2. There is no predefined Entrypoint or default command
- R3. The rock must have version 6.0 of the .NET Runtime installed
- R4. ``/usr/bin/dotnet`` must be a symbolic link to the .NET binary

With these requirements in mind, and in the same directory as the Dockerfile
from above, write the following into a text editor and save it as
``rockcraft.yaml``:

.. literalinclude:: ../code/migrate-to-chiselled-rock/rockcraft.yaml
    :caption: rockcraft.yaml
    :language: yaml

Note the subtle chiselling of the .NET Runtime package in ``rockcraft.yaml``.
You are requesting Rockcraft to install the ``libs`` slice of the
``dotnet-runtime`` deb, which is defined in the
`ubuntu-22.04 Chisel release
<https://github.com/canonical/chisel-releases/tree/ubuntu-22.04/slices/>`_.


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
    :emphasize-lines: 42
    :class: log-snippets

    2023-04-19 15:52:48.045 Starting Rockcraft 0.0.1.dev1
    ...
    2023-04-19 15:52:48.214 Launching instance...
    2023-04-19 15:52:48.214 Executing on host: lxc remote list --format=yaml
    ...
    2023-04-19 15:58:25.138 :: 2023-04-19 13:56:57.784 Executing parts lifecycle: build install-dotnet-runtime
    2023-04-19 15:58:25.138 :: 2023-04-19 13:56:57.784 Executing action
    2023-04-19 15:58:25.138 :: 2023-04-19 13:56:57.784 execute action install-dotnet-runtime:Action(part_name='install-dotnet-runtime', step=Step.BUILD, action_type=ActionType.RUN, reason=None, project_vars=None, properties=ActionProperties(changed_files=None, changed_dirs=None))
    2023-04-19 15:58:25.138 :: 2023-04-19 13:56:57.785 load state file: /root/parts/install-dotnet-runtime/state/pull
    2023-04-19 15:58:25.138 :: 2023-04-19 13:56:58.081 :: 2023/04/19 13:56:58 Consulting release repository...
    2023-04-19 15:58:25.138 :: 2023-04-19 13:56:58.349 :: 2023/04/19 13:56:58 Fetching current ubuntu-22.04 release...
    2023-04-19 15:58:25.138 :: 2023-04-19 13:56:58.351 :: 2023/04/19 13:56:58 Processing ubuntu-22.04 release...
    2023-04-19 15:58:25.138 :: 2023-04-19 13:56:58.369 :: 2023/04/19 13:56:58 Selecting slices...
    2023-04-19 15:58:25.138 :: 2023-04-19 13:56:58.369 :: 2023/04/19 13:56:58 Fetching ubuntu 22.04 jammy suite details...
    2023-04-19 15:58:25.138 :: 2023-04-19 13:57:04.548 :: 2023/04/19 13:57:04 Release date: Thu, 21 Apr 2022 17:16:08 UTC
    2023-04-19 15:58:25.138 :: 2023-04-19 13:57:04.549 :: 2023/04/19 13:57:04 Fetching index for ubuntu 22.04 jammy main component...
    2023-04-19 15:58:25.138 :: 2023-04-19 13:57:05.684 :: 2023/04/19 13:57:05 Fetching index for ubuntu 22.04 jammy universe component...
    2023-04-19 15:58:25.138 :: 2023-04-19 13:57:25.215 :: 2023/04/19 13:57:25 Fetching ubuntu 22.04 jammy-security suite details...
    2023-04-19 15:58:25.138 :: 2023-04-19 13:57:25.289 :: 2023/04/19 13:57:25 Release date: Wed, 19 Apr 2023 12:55:48 UTC
    2023-04-19 15:58:25.139 :: 2023-04-19 13:57:25.289 :: 2023/04/19 13:57:25 Fetching index for ubuntu 22.04 jammy-security main component...
    2023-04-19 15:58:25.139 :: 2023-04-19 13:57:30.489 :: 2023/04/19 13:57:30 Fetching index for ubuntu 22.04 jammy-security universe component...
    2023-04-19 15:58:25.139 :: 2023-04-19 13:57:32.522 :: 2023/04/19 13:57:32 Fetching ubuntu 22.04 jammy-updates suite details...
    2023-04-19 15:58:25.139 :: 2023-04-19 13:57:32.667 :: 2023/04/19 13:57:32 Release date: Wed, 19 Apr 2023 13:29:07 UTC
    2023-04-19 15:58:25.139 :: 2023-04-19 13:57:32.668 :: 2023/04/19 13:57:32 Fetching index for ubuntu 22.04 jammy-updates main component...
    2023-04-19 15:58:25.139 :: 2023-04-19 13:57:33.631 :: 2023/04/19 13:57:33 Fetching index for ubuntu 22.04 jammy-updates universe component...
    2023-04-19 15:58:25.139 :: 2023-04-19 13:57:37.908 :: 2023/04/19 13:57:37 Fetching pool/main/b/base-files/base-files_12ubuntu4.3_amd64.deb...
    2023-04-19 15:58:25.139 :: 2023-04-19 13:57:38.157 :: 2023/04/19 13:57:38 Fetching pool/main/g/glibc/libc6_2.35-0ubuntu3.1_amd64.deb...
    2023-04-19 15:58:25.139 :: 2023-04-19 13:57:40.834 :: 2023/04/19 13:57:40 Fetching pool/main/g/gcc-12/libgcc-s1_12.1.0-2ubuntu1~22.04_amd64.deb...
    2023-04-19 15:58:25.140 :: 2023-04-19 13:57:41.262 :: 2023/04/19 13:57:41 Fetching pool/main/g/gcc-12/libstdc++6_12.1.0-2ubuntu1~22.04_amd64.deb...
    2023-04-19 15:58:25.140 :: 2023-04-19 13:57:42.001 :: 2023/04/19 13:57:42 Fetching pool/universe/d/dotnet6/dotnet-host_6.0.116-0ubuntu1~22.04.1_amd64.deb...
    2023-04-19 15:58:25.140 :: 2023-04-19 13:57:42.119 :: 2023/04/19 13:57:42 Fetching pool/universe/d/dotnet6/dotnet-hostfxr-6.0_6.0.116-0ubuntu1~22.04.1_amd64.deb...
    2023-04-19 15:58:25.140 :: 2023-04-19 13:57:42.237 :: 2023/04/19 13:57:42 Fetching pool/main/i/icu/libicu70_70.1-2_amd64.deb...
    2023-04-19 15:58:25.140 :: 2023-04-19 13:57:44.046 :: 2023/04/19 13:57:44 Fetching pool/main/u/ust/liblttng-ust-common1_2.13.1-1ubuntu1_amd64.deb...
    2023-04-19 15:58:25.140 :: 2023-04-19 13:57:44.146 :: 2023/04/19 13:57:44 Fetching pool/main/n/numactl/libnuma1_2.0.14-3ubuntu2_amd64.deb...
    2023-04-19 15:58:25.141 :: 2023-04-19 13:57:44.247 :: 2023/04/19 13:57:44 Fetching pool/main/u/ust/liblttng-ust-ctl5_2.13.1-1ubuntu1_amd64.deb...
    2023-04-19 15:58:25.141 :: 2023-04-19 13:57:44.355 :: 2023/04/19 13:57:44 Fetching pool/main/u/ust/liblttng-ust1_2.13.1-1ubuntu1_amd64.deb...
    2023-04-19 15:58:25.141 :: 2023-04-19 13:57:44.571 :: 2023/04/19 13:57:44 Fetching pool/main/o/openssl/libssl3_3.0.2-0ubuntu1.8_amd64.deb...
    2023-04-19 15:58:25.141 :: 2023-04-19 13:57:45.111 :: 2023/04/19 13:57:45 Fetching pool/main/l/llvm-toolchain-13/libunwind-13_13.0.1-2ubuntu2.1_amd64.deb...
    2023-04-19 15:58:25.141 :: 2023-04-19 13:57:45.213 :: 2023/04/19 13:57:45 Fetching pool/main/x/xz-utils/liblzma5_5.2.5-2ubuntu1_amd64.deb...
    2023-04-19 15:58:25.141 :: 2023-04-19 13:57:53.384 :: 2023/04/19 13:57:53 Fetching pool/main/libu/libunwind/libunwind8_1.3.2-2build2_amd64.deb...
    2023-04-19 15:58:25.141 :: 2023-04-19 13:57:53.523 :: 2023/04/19 13:57:53 Fetching pool/main/z/zlib/zlib1g_1.2.11.dfsg-2ubuntu9.2_amd64.deb...
    2023-04-19 15:58:25.141 :: 2023-04-19 13:57:53.982 :: 2023/04/19 13:57:53 Fetching pool/universe/d/dotnet6/dotnet-runtime-6.0_6.0.116-0ubuntu1~22.04.1_amd64.deb...
    ...
    2023-04-19 15:56:00.566 :: 2023-04-19 13:55:59.756 Created new layer
    2023-04-19 15:56:00.566 :: 2023-04-19 13:55:59.758 Adding Pebble entrypoint
    2023-04-19 15:56:00.566 :: 2023-04-19 13:55:59.758 Configuring entrypoint...
    2023-04-19 15:56:00.567 :: 2023-04-19 13:55:59.767 Entrypoint set to ['/bin/pebble', 'enter']
    2023-04-19 15:56:00.567 :: 2023-04-19 13:55:59.767 Adding metadata
    2023-04-19 15:56:00.567 :: 2023-04-19 13:55:59.767 Configuring labels and annotations...
    2023-04-19 15:56:00.567 :: 2023-04-19 13:55:59.785 Labels and annotations set to ['org.opencontainers.image.version=chiselled', 'org.opencontainers.image.title=dotnet-runtime', 'org.opencontainers.image.ref.name=dotnet-runtime', 'org.opencontainers.image.licenses=Apache-2.0', 'org.opencontainers.image.created=2023-04-19T13:55:59.767870+00:00', 'org.opencontainers.image.base.digest=13155b5ad26816d4107ee499de072069a701c9fe183f7e347e8d88fee16e69c2']
    2023-04-19 15:56:00.567 :: 2023-04-19 13:55:59.792 Setting the ROCK's Control Data
    2023-04-19 15:56:00.567 :: 2023-04-19 13:55:59.797 Adding to layer: /tmp/tmpdqjmducj/.rock as '.rock'
    2023-04-19 15:56:00.567 :: 2023-04-19 13:55:59.797 Adding to layer: /tmp/tmpdqjmducj/.rock/metadata.yaml as '.rock/metadata.yaml'
    2023-04-19 15:56:00.567 :: 2023-04-19 13:55:59.803 Control data written
    2023-04-19 15:56:00.567 :: 2023-04-19 13:55:59.804 Metadata added
    2023-04-19 15:56:00.567 :: 2023-04-19 13:55:59.804 Exporting to OCI archive
    2023-04-19 15:56:00.567 :: 2023-04-19 13:56:00.148 Exported to OCI archive 'dotnet-runtime_chiselled_amd64.rock'

At the end of the process, a file named ``dotnet-runtime_chiselled_amd64.rock``
should be present in the current directory. That's your chiselled rock,
as an OCI archive.


Test the rock
-------------

First, import the recently created rock into Docker:

.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:skopeo-copy]
    :end-before: [docs:skopeo-copy-end]
    :dedent: 2

Now inspect the chiselled .NET Runtime rock the same way as it was done for the
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

    REPOSITORY TAG IMAGE ID CREATED SIZE
    dotnet-runtime   chiselled   4e0951d180e3   About a minute ago   124MB

And make sure this rock is as functional as the reference Docker image:

.. literalinclude:: ../code/migrate-to-chiselled-rock/task.yaml
    :language: bash
    :start-after: [docs:run-rock]
    :end-before: [docs:run-rock-end]
    :dedent: 2

The output should be similar to:

..  code-block:: text
    :emphasize-lines: 13
    :class: log-snippets

    global.json file:
    Not found

    Host:
    Version:6.0.16
    Architecture: x64
    Commit: 1e620a42e7

    .NET SDKs installed:
    No SDKs were found.

    .NET runtimes installed:
    Microsoft.NETCore.App 6.0.16 [/usr/lib/dotnet/shared/Microsoft.NETCore.App]

    Download .NET:
    https://aka.ms/dotnet-download

    Learn about .NET Runtimes and SDKs:
    https://aka.ms/dotnet/runtimes-sdk-info


Conclusion
----------

In this tutorial, you have migrated from an imperative container build
instructions (Dockerfile) to a declarative one (``rockcraft.yaml``), without any
overhead on the final file's size or complexity.

The resulting rock ended up being 63MB smaller than the reference one, while
offering the same .NET Runtime functionality.

.. _Microsoft's .NET Runtime 6.0: https://github.com/dotnet/dotnet-docker/tree/36e80c363f5fa5a4f20d004c759c932a4027c89b/src/runtime/6.0/jammy
