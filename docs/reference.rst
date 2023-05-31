.. _reference:

*********
Reference
*********


A Rockcraft project is defined in a YAML file named ``rockcraft.yaml``
at the root of the project tree in the filesystem.

This `Reference`_ section is for when you need to know which options can be
used, and how, in this ``rockcraft.yaml`` file.


Format specification
--------------------

.. code-block:: yaml

  # The name of the ROCK.
  name: <name>

  # (Optional) The human-readable title of the ROCK. Defaults to name.
  title: <title>

  # Short summary describing the ROCK.
  summary: <summary>

  # Long multi-line description of the ROCK.
  description: |
    <description>

  # The ROCK version, used within the ROCK OCI tag.
  version: <version>

  # The system image and version the application will be layered on.
  base: ubuntu:18.04 | ubuntu:20.04 | ubuntu:22.04 | bare

  # (Optional) The system and version on top of which the application
  # will be built. Defaults to base.
  build-base: ubuntu:18.04 | ubuntu:20.04 | ubuntu:22.04

  # The license, in SPDX format, of the software packaged inside the ROCK.
  # This field is case insensitive.
  license: <license>

  # (Optional) A list of services for the Pebble entrypoint.
  # The syntax follows the Pebble layer specification in
  # https://github.com/canonical/pebble#layer-specification
  services:
    <service name>:
      # Each Pebble service definition must have these two fields
      override: merge | replace
      command: <command>
      # (Optional) Other configurations for the Pebble service
      <key>: <value>

  # List of architecture-specific ROCKs to be built.
  # Supported architectures are: amd64, arm64, arm, i386, ppc64le, riscv64 and s390x.
  platforms:
    # If matching a valid architecture name, it must be the same as "build-for".
    <entry>:
      # Host architectures where the ROCK can be built.
      # Required when "build-for" is specified, otherwise it defaults to <entry>
      build-on: [<arch>, ...]
      # (Optional) Target architecture the ROCK will be built for.
      # Defaults to <entry>.
      build-for: <arch>

  # The parts used to build the application.
  parts:
    <part name>:
      ...

.. note::
   The fields ``entrypoint``, ``cmd`` and ``env`` are not supported in
   Rockcraft. All ROCKs have Pebble as their entrypoint, and thus you must use
   ``services`` to define your container application.


Example
.......

.. code-block:: yaml

  name: hello
  title: Hello World
  summary: An Hello World ROCK
  description: |
    This is just an example of a Rockcraft project
    for a Hello World ROCK.
  version: latest
  base: bare
  build-base: ubuntu:22.04
  license: Apache-2.0
  services:
    hello:
      override: replace
      command: /usr/bin/hello -t
      environment:
        VAR1: value
        VAR2: "other value"
  platforms:
    amd64:
    arm:
      build-on: ["arm", "arm64"]
    ibm:
      build-on: ["s390x"]
      build-for: s390x

  parts:
    hello:
      plugin: nil
      stage-packages:
        - hello

Rockcraft parts
---------------

.. rubric:: The main building blocks of a ROCK are *parts*.

If this sentence sounds familiar, it's because **it is familiar**!
Rockcraft parts are inherited from other existing Craft tools like
`Snapcraft <https://github.com/snapcore/snapcraft>`_ and
`Charmcraft <https://github.com/canonical/charmcraft>`_.

Rockcraft *parts* go through the same lifecycle steps as Charmcraft and
`Snapcraft parts <https://snapcraft.io/docs/parts-lifecycle>`_.

The way the *parts*' keys and values are used in the *rockcraft.yaml* is exactly
the same as in `snapcraft.yaml`_
(`here <https://snapcraft.io/docs/adding-parts>`_ is how you define a *part*).

Albeit being fundamentally identical to Snapcraft parts, Rockcraft parts
actually offer some extended functionality and keywords:

* **stage-packages**: apart from offering the well-known package installation
  behavior, in Rockcraft the ``stage-packages`` keyword actually supports
  chiseled packages as well (:ref:`learn more about Chisel
  <chisel_explanation>`).
  To install a package slice instead of the whole package, simply follow the
  Chisel convention *<packageName>_<sliceName>*.


Example
.......

.. _chisel-example:

.. code-block:: yaml

  parts:
    chisel-openssl-binaries-only:
      plugin: nil
      stage-packages:
        - openssl_bins
        - ca-certificates_data

    package-hello:
      plugin: nil
      stage-packages:
        - hello


NOTE: at the moment, it is not possible to mix packages and slices in the same
stage-packages field.


Rockcraft commands
------------------
Lifecycle commands
..................
Lifecycle commands can take an optional parameter ``<part-name>``. When a part
name is provided, the command applies to the specific part. When no part name is
provided, the command applies to all parts.

clean
^^^^^
Removes a part's assets. When no part is provided, the entire build environment
(e.g. the LXD instance) is removed.

pull
^^^^
Downloads or retrieves artifacts defined for each part.

overlay
^^^^^^^
Execute operations defined for each part on a layer over the base filesystem,
potentially modifying its contents.

build
^^^^^
Builds artifacts defined for each part.

stage
^^^^^
Stages built artifacts into a common staging area, for each part.

prime
^^^^^
Prepare, for each part, the final payload to be packed as a ROCK, performing
additional processing and adding metadata files.

pack
^^^^
*This is the default lifecycle command for* ``rockcraft``.

Process parts and create the ROCK as an OCI archive file containing the project
payload with the provided metadata.

Other commands
..............
init
^^^^
Initializes a rockcraft project with a boilerplate ``rockcraft.yaml`` file.

help
^^^^
Shows information about a command.

.. _snapcraft.yaml: https://snapcraft.io/docs/snapcraft-parts-metadata

