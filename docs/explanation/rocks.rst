.. _rocks_explanation:

ROCKs
=====

ROCKs are **Ubuntu LTS-based container images** that are designed to meet
cloud-native software's security, stability, and reliability requirements.

ROCKs comply with the `Open Container Initiative`_'s (OCI) `image format
specification <OCI_image_spec_>`_, and can be stored in any OCI-compliant
container registry (e.g. DockerHub, ECR, ACR,..) and used by any OCI-compliant
tool (e.g. Docker, Podman, Kubernetes,...).

Interoperability between ROCKs and other containers also extends to how
container images are built. This enables using ROCKs as bases for existing
build recipes, such as Dockerfiles, for further customisation and development.

What sets ROCKs apart?
~~~~~~~~~~~~~~~~~~~~~~

* **Opinionated and consistent design**: all ROCKs follow the same design,
  aiming to minimise your full-stack disparity and adoption overhead, i.e

  * :ref:`pebble_explanation_page` **is the official entrypoint for all
    ROCKs**, thus providing a predictable and powerful abstraction layer
    between the user and the container application;
  * ROCKs extend the OCI image information by including additional **metadata**
    inside each ROCK (e.g. at ``/.rock/metadata.yaml``), allowing container
    applications to easily inspect the properties of the image they are running
    on, at execution time;
* **User-centric experience**: ROCKs are described in a :ref:`declarative
  format<rockcraft.yaml_reference>` and **built on top of familiar and reliable
  Ubuntu LTS images**, thus offering an open and up-to-date user experience;
* **Seamless chiselling experience**: ROCKs can be effortlessly
  :ref:`chiselled<chisel_explanation>` using off-the-shelf primitives,
  harnessing all the advantageous traits of "distroless" to deliver **compact
  and secure Ubuntu-based container images**.


Design
~~~~~~

Given their compliance with the `OCI image specification <OCI_image_spec_>`_,
all ROCKs are constituted by OCI metadata (like the image's index, manifest and
configuration) plus the actual `OCI layers`_ with the container filesystem
contents.

.. figure:: /_static/rock_diagram.png
   :width: 75%
   :align: center
   :alt: ROCK diagram
