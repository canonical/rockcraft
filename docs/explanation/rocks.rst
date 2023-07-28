.. _rocks_explanation:

ROCKs
=====

ROCKs are Ubuntu-based container images that are designed to meet
cloud-native software's security, stability, and reliability requirements.

ROCKs were created with a focus on those values:

* **Developers experience**: Rockcraft uses a declarative format to describe
  ROCKs, aiming to simplify container image definition and provide the best
  user experience.
* **Ubuntu Experience**: Built on top of Ubuntu, ROCKs provide reliability
  and stability to users. They offer access to the latest features, ensuring
  users can meet their needs. With long-term support (LTS), ROCKs images
  are regularly updated.
* **Consistency**: ROCKs are consistent by utilising Pebble as the entrypoint.
  Learning Pebble allows you to interact smoothly with all the ROCKs.

ROCKs comply with the `Open Container
Initiative`_ (OCI) `image format specification <OCI_image_spec_>`_.
ROCKs can be stored in container registries (e.g. DockerHub, ECR, ACR,..)
and used with any OCI-Compliant tools (e.g. Docker, Podman, Kubernetes,...).

Interoperability between ROCKs and other containers also extends to how
container images are built. This enables using ROCKs as bases for
existing build recipes, such as Dockerfiles, for further customisation and
development.

The ROCKs ecosystem comprises

.. figure:: /_static/rockcraft_diagram.jpg
   :width: 75%
   :align: center
   :alt: ROCKs ecosystem


Chisel
------

Chisel is a software tool for extracting well-defined portions
(also known as slices)  of Debian packages into a filesystem.
To learn more about Chisel see: :ref:`chisel_explanation`

Pebble
------

In ROCKS, Pebble is the default entrypoint (an executable that
runs when the container is initiated) in ROCKS, ensuring consistent
container inspection and permit to have multiple entrypoint
without the need to create other files.To learn more about
Pebble see: :ref:`pebble_explanation_page`

Rockcraft
---------

Rockcraft is a tool designed to build ROCKs using a declarative syntax
(yaml). It leverages the logic of plugins, parts,and concepts that exist
in Snapcraft and Charmcraft.

Developers familiar with the creation and publication of snaps and charms
will be able to utilise existing knowledge to create ROCKS.
To learn why you need to use Rockcraft see: :ref:`why_use_rockcraft`
