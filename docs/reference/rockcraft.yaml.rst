
**************
rockcraft.yaml
**************

A Rockcraft project is defined in a YAML file named ``rockcraft.yaml``
at the root of the project tree in the filesystem.

This Reference section is for when you need to know which options can be
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
