*********
Reference
*********

Rockcraft.yaml format
=====================

A Rockcraft project is defined in a YAML file named ``rockcraft.yaml``
at the root of the project tree in the filesystem.


Format specification
--------------------

.. code-block:: yaml

  # The name of the ROCK project.
  name: <name>
  
  # The project version, used as the container tag.
  version: <version>
  
  # The system image and version the application will be layered on.
  base: ubuntu:18.04 | ubuntu:20.04
  
  # (Optional) The system and version on top of which the application
  # will be built. Defaults to base.
  build-base: <base>
  
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
  
  # The parts used to build the application.
  parts:
    <part name>:
      ...
  

Example
-------

.. code-block:: yaml

  name: hello 
  version: latest
  base: ubuntu:20.04
  entrypoint: [/usr/bin/hello, -t]
  env:
    - VAR1: value
    - VAR2: "other value"
  
  parts:
    hello:
      plugin: nil
      overlay-packages:
        - hello
