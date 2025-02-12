.. _rocks_explanation:

Rocks
=====

Rocks are **Ubuntu LTS-based container images** that are designed to meet
cloud-native software's security, stability, and reliability requirements.

Rocks comply with the `Open Container Initiative`_'s (OCI) `image format
specification <OCI_image_spec_>`_, and can be stored in any OCI-compliant
container registry (e.g. DockerHub, ECR, ACR,..) and used by any OCI-compliant
tool (e.g. Docker, Podman, Kubernetes,...).

Interoperability between rocks and other containers also extends to how
container images are built, allowing rocks to be used as bases for existing
build instructions, such as Dockerfiles, for further customisation and
development.

.. _what-sets-rocks-apart:

What sets rocks apart?
~~~~~~~~~~~~~~~~~~~~~~

* **Opinionated and consistent design**: all rocks follow the same design,
  aiming to minimise your full-stack disparity and adoption overhead, e.g.

  * :ref:`pebble_explanation_page` **is the official entrypoint for all
    rocks**, providing a predictable and powerful abstraction layer
    between the user and the container application;
  * Rocks extend the OCI image information by including additional **metadata**
    inside each rock (e.g. at ``/.rock/metadata.yaml``), allowing container
    applications to easily inspect the properties of the image they are running
    on, at execution time;
* **User-centric experience**: rocks are described in a :ref:`declarative
  format<rockcraft.yaml_reference>` and **built on top of familiar and reliable
  Ubuntu LTS images**, offering an open and up-to-date user experience;
* **Seamless chiselling experience**: rocks can be effortlessly
  :ref:`chiselled<chisel_explanation>` using off-the-shelf primitives,
  harnessing all the advantages of "distroless" to deliver **compact
  and secure Ubuntu-based container images**.


Design
~~~~~~

Given their compliance with the `OCI image specification <OCI_image_spec_>`_,
all rocks are constituted by OCI metadata (like the image's `index`_,
`manifest`_ and `configuration`_) plus the actual `OCI layers`_ with the
container filesystem contents.

Typically, container users won't be directly building or accessing the raw OCI
components that form an image. However, these are frequently used as the
underlying source of truth when inspecting container images with tools like
`Docker`_ or `skopeo`_. As an example, the command ``docker inspect`` will,
in general, source the requested information from the image's OCI
`configuration`_.

On the other hand, the `OCI layers`_ are the literal filesystem contents that
result from the user's instructions at image build time, and that can be
accessed by the container application at runtime.

The following diagram depicts the different OCI components in the context of a
rock, highlighting where the aforementioned design features (like the Pebble
entrypoint) fit in.

.. figure:: /_static/rock_diagram.png
   :width: 75%
   :align: center
   :alt: Rock diagram

.. _`index`: https://github.com/opencontainers/image-spec/blob/main/image-index.md
.. _`manifest`: https://github.com/opencontainers/image-spec/blob/main/manifest.md
.. _`configuration`: https://github.com/opencontainers/image-spec/blob/main/config.md
