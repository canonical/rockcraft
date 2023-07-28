.. _pebble_explanation_page:

Pebble
======

.. important::
    **Pebble is the default entrypoint for all ROCKs!**

Similar to other well-known process managers such as *supervisord*, *runit*, or
*s6*, Pebble is a service manager that enables the seamless orchestration of a
collection of local service processes as a cohesive unit (i.e. an organized set
of processes). The main difference is that Pebble has been designed with
custom-tailored features that significantly enhance the overall container
experience, making it the ideal candidate for the container's init process
(also known as the entrypoint, with PID=1). 

Multiple processes in a container?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Containers' best practices dictate it is better to separate areas of concern
and have one service per container. The introduction of Pebble as the ROCKs'
entrypoint elevates this notion such that:

  if multiple processes have shared dependencies and must always be executed
  together, then it is best practice to orchestrate them within the same
  container.


Features
~~~~~~~~


When creating container images, several issues can be met.
For instance, if the entrypoint relies on the application mode
(such as nginx and nginx-debug), creating a bash script that parses all the
arguments provided during container deployment will be necessary.
Additionally, each image runs with specific application arguments,
making it challenging to perform an inspection inside the image consistently.

Pebble solves these problems by providing a comprehensive set of commands
for starting, stopping, and viewing service status. It also includes features
like auto-restart for continuous operation and dependency management for
properly sequencing services. Pebble streamlines service management as a
single binary that operates as a background service and a client.

In ROCKs, Pebble services are defined with properties such as name, command,
startup behaviour, dependencies,... Moreover, Pebble is the default entrypoint
(an executable that runs when the container is initiated) in ROCKs, ensuring
consistent container inspection and permit to have multiple entrypoint
without the need to create other files.


Create a service
----------------

See :doc:`/how-to/convert-to-pebble-layer` for information about converting
a Docker entrypoint to a pebble service. Also, check the top-level field
on :doc:`/reference/rockcraft.yaml` to understand the parameters and fields
needed to create a service.

