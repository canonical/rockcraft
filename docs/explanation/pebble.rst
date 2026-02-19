.. _explanation-pebble:

Pebble
======

.. important::

    Pebble is the default entrypoint for all rocks.

Similar to other well-known process managers such as *supervisord*, *runit*, or
*s6*, `Pebble`_ is a service manager that enables the seamless orchestration of
a collection of local service processes as an organised set. The main difference
is that `Pebble`_ has been designed with custom-tailored features that
significantly enhance the overall container experience, making it the ideal
candidate for the container's init process (also known as the entrypoint,
with PID=1).

Multiple processes in a container?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Containers' best practices advocate the separation of concerns and the adoption
of a single service per container. With the introduction of `Pebble`_ as the
rocks' entrypoint, this principle is elevated to new heights:

    If multiple processes rely on shared dependencies and are tightly coupled
    together (i.e. they serve a single purpose and cannot be executed
    independently), then the best practice entails orchestrating them within the
    same container, with Pebble as their manager.

This new notion addresses existing pain points arising from the excessive
separation of concerns, which results in numerous container images whose
entrypoints lack the ability to gracefully handle the underlying child
processes. This is one of the main reasons behind the gradual shift in the best
practices, as there is an increasing emphasis on adopting init processes such
as `tini`_, `s6-overlay`_, or `Pebble`_.

What to expect?
~~~~~~~~~~~~~~~

Pebble distinguishes itself from other similar tools (like `tini`_ and
`s6-overlay`_) by offering the following core features:

* **client-server model behind a single binary**: Pebble is injected into
  rocks as a single binary which acts both as a daemon and a client to itself;
* **declarative service definition**: the Pebble service processes (or simply
  *Pebble services*) are declaratively defined in YAML files called layers.
  Compared to `imperative wrapper scripts (as suggested in the Docker
  documentation)`_, this provides a much cleaner and less error-prone way
  to define the processes that should run inside the container.
* **services as first-class citizens**: unlike wrapper scripts, Pebble
  treats services as manageable units with a defined lifecycle and
  service-specific definitions for health monitoring, inter-service
  dependencies, restart policies, and much more;
* **layering**: Pebble can stack multiple layers (represented as YAML files)
  into a single Pebble plan where all services are defined. With this layering
  mechanism, existing services can be overridden or re-configured;
* **container-optimised init process**: as a rock's PID 1, Pebble acts as an
  init process and thus offers:

  * support for multiple child processes,
  * reaping and subreaping,
  * signal forwarding,
  * graceful shutdown,
  * log rotation,
  * run the Pebble daemon and client commands in a single operation;
* **consistent user experience**: since every rock has Pebble as its
  entrypoint, a predictable and consistent user experience is guaranteed;
* **embedded utilities**: regardless of the rock's contents, Pebble offers a
  comprehensive suite of commands for inspecting and interacting with the
  container. These commands are especially useful for :ref:`chiseled rocks
  <explanation-chisel>`, as they encompass functionalities such as listing and
  deleting files, creating directories, and inspecting Pebble services,
  among others.

Creating services
~~~~~~~~~~~~~~~~~

Rockcraft follows the :external+pebble:ref:`Pebble layer specification
<layer-specification>` to the letter, with Pebble services defined in
:ref:`reference-rockcraft-yaml`. :ref:`how-to-convert-an-entrypoint-to-a-pebble-layer`
provides an example of how to convert a Docker entrypoint to a Pebble layer.


.. _Pebble: https://documentation.ubuntu.com/pebble/
.. _tini: https://github.com/krallin/tini
.. _s6-overlay: https://github.com/just-containers/s6-overlay
.. _imperative wrapper scripts (as suggested in the Docker documentation): https://docs.docker.com/engine/containers/multi-service_container/#use-a-wrapper-script
