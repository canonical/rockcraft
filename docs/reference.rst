*********
Reference
*********


A Rockcraft project is defined in a YAML file named ``rockcraft.yaml``
at the root of the project tree in the filesystem.

This `Reference`_ section is for when you need to know which options can be used, and how, in this ``rockcraft.yaml`` file.


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
  base: ubuntu:18.04 | ubuntu:20.04 | ubuntu:22:04 | bare
  
  # (Optional) The system and version on top of which the application
  # will be built. Defaults to base.
  build-base: ubuntu:18.04 | ubuntu:20.04 | ubuntu:22:04
  
  # The license, in SPDX format, of the software packaged inside the ROCK.
  # This field is case insensitive.
  license: <license>

  # (Optional) The container entry point.
  entrypoint: [<path>, ...]
  
  # (Optional) The container command line, used as arguments for
  # entrypoint. If the entrypoint is not defined, the first item in
  # the cmd list the command to execute.
  cmd: [<arg>, ...]
  
  # (Optional) A list of keys and values defining the container's
  # runtime environment variables.
  env:
    - <var name>: <value>

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


Example
.......

.. code-block:: yaml

  name: hello 
  title: Hello World
  summary: An Hello World ROCK
  description: |
    This is just an example of a Rockcraft project
    for an Hello World ROCK.
  version: latest
  base: bare
  build-base: ubuntu:22.04
  license: Apache-2.0
  entrypoint: [/usr/bin/hello, -t]
  env:
    - VAR1: value
    - VAR2: "other value"
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
