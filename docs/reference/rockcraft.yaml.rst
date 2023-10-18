.. _rockcraft.yaml_reference:

**************
rockcraft.yaml
**************

A Rockcraft project is defined in a YAML file named ``rockcraft.yaml``
at the root of the project tree in the filesystem.

This Reference section is for when you need to know which options can be
used, and how, in this ``rockcraft.yaml`` file.


Format specification
====================

``name``
--------

**Type**: string

**Required**: Yes

The name of the ROCK. This value must conform with Pebble's format for layer
files, meaning that the ``name``:

- must start with a lowercase letter [a-z];
- must contain only lowercase letters [a-z], numbers [0-9] or hyphens;
- must not end with a hyphen, and must not contain two or more consecutive
  hyphens.

``title``
---------

**Type**: string

**Required**: No

The human-readable title of the ROCK. If omitted, defaults to ``name``.

``summary``
-----------

**Type**: string

**Required**: Yes

A short summary describing the ROCK.

``description``
---------------

**Type**: string

**Required**: Yes

A longer, possibly multi-line description of the ROCK.

``version``
-----------

**Type**: string

**Required**: Yes

The ROCK version, used to tag the OCI image and name the ROCK file.

``base``
--------

**Type**: One of ``ubuntu:18.04 | ubuntu:20.04 | ubuntu:22.04 | bare``

**Required**: Yes

The base system image that the ROCK's contents will be layered on. This is also
the system that will be mounted and made available when using Overlays. The
special value ``bare`` means that the ROCK will have no base system at all,
which is typically used with static binaries or
:ref:`Chisel slices <chisel_explanation>`.

``build-base``
--------------

**Type**: One of ``ubuntu:18.04 | ubuntu:20.04 | ubuntu:22.04``

**Required**: Yes, if ``base`` is ``bare``

The system and version that will be used during the ROCK's build, but not
included in the final ROCK itself. It comprises the set of tools and libraries
that Rockcraft will use when building the ROCK's contents. This field is
mandatory if ``base`` is ``bare``, but otherwise it is optional and defaults to
the value of ``base``.

``license``
-----------

**Type**: string, in `SPDX format <https://spdx.org/licenses/>`_

**Required**: Yes

The license of the software packaged inside the ROCK. This must match the SPDX
format, but is case insensitive (e.g. both ``MIT`` and ``mit`` are valid).

``run-user``
------------

**Type**: string

**Required**: No

The default OCI user. It must be a supported shared user. Currently, the only
supported shared user is "_daemon_" (with UID/GID 584792). It defaults to
"root" (with UID 0).

``environment``
---------------

**Type**: dict

**Required**: No

A set of key-value pairs specifying the environment variables to be added
to the base image's OCI environment.

.. note::
   String interpolation is not yet supported so any attempts to dynamically
   define environment variables with ``$`` will end in a project
   validation error.

``services``
------------

**Type**: dict, following the `Pebble Layer Specification format`_

**Required**: No

A list of services for the Pebble entrypoint. It uses Pebble's layer
specification syntax exactly, with each entry defining a Pebble service. For
each service, the ``override`` and ``command`` fields are mandatory, but all
others are optional.

``checks``
------------

**Type**: dict, following the `Pebble Layer Specification format`_

**Required**: No

A list of health checks that can be configured to restart Pebble services
when they fail. It uses Pebble's layer specification syntax, with each
entry corresponding to a check. Each check can be one of three types:
``http``, ``tcp`` or ``exec``.

``platforms``
-------------

**Type**: dict

**Required**: Yes

The set of architecture-specific ROCKs to be built. Supported architectures are:
``amd64``, ``arm64``, ``armhf``, ``i386``, ``ppc64el``, ``riscv64`` and ``s390x``.

Entries in the ``platforms`` dict can be free-form strings, or the name of a
supported architecture (in Debian format).

.. warning::
   **All** target architectures must be compatible with the architecture of
   the host where Rockcraft is being executed (i.e. emulation is not supported
   at the moment).

``platforms.<entry>.build-on``
------------------------------

**Type**: list[string]

**Required**: Yes, if ``build-for`` is specified *or* if ``<entry>`` is not a
supported architecture name.

Host architectures where the ROCK can be built. Defaults to ``<entry>`` if that
is a valid, supported architecture name.

``platforms.<entry>.build-for``
-------------------------------

**Type**: string | list[string]

**Required**: Yes, if ``<entry>`` is not a supported architecture name.

Target architecture the ROCK will be built for. Defaults to ``<entry>`` that
is a valid, supported architecture name.

.. note::
   At the moment Rockcraft will only build for a single architecture, so
   if provided ``build-for`` must be a single string or a list with exactly one
   element.

``parts``
---------

**Type**: dict

**Required**: Yes

The set of parts that compose the ROCK's contents
(see :ref:`Parts <ref_parts>`).


.. note::
   The fields ``entrypoint``, ``cmd`` and ``env`` are not supported in
   Rockcraft. All ROCKs have Pebble as their entrypoint, and thus you must use
   ``services`` to define your container application.


Example
=======

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
  run-user: _daemon_
  environment:
    FOO: bar
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


.. _`Pebble Layer Specification format`:  https://github.com/canonical/pebble#layer-specification
