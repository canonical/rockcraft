.. _explanation_cryptographic-technology:

Cryptographic technology in Rockcraft
=====================================

Rockcraft uses cryptographic technologies to fetch arbitrary files over the internet,
communicate with local processes, and store credentials. It does not directly implement
its own cryptography, but it does depend on external libraries to do so.

Rockcraft is built upon `Craft Application`_ and derives much of its functionality from
it, so much of Rockcraft's cryptographic functionality is described in `Cryptographic
technology in Craft Application`_. The additional cryptography functionality in
Rockcraft is documented below.

OCI image manipulation
~~~~~~~~~~~~~~~~~~~~~~

Every installation of Rockcraft comes with a bundled copy of `umoci`_. Internally, umoci
is used to create and manipulate container images as part of the rock building process.
Rockcraft only uses the internal, pre-packaged copy of umoci for this purpose.

Container image registries
~~~~~~~~~~~~~~~~~~~~~~~~~~

Every installation of Rockcraft comes with a bundled copy of `skopeo`_. This tool is
available to run as ``rockcraft.skopeo`` for creating local container image registries
during development. Skopeo is additionally used internally as part of the rock building
process. Rockcraft only uses the internal, pre-packaged copy of skopeo for this purpose.

.. _Craft Application: https://canonical-craft-application.readthedocs-hosted.com/en/latest/
.. _Cryptographic technology in Craft Application: https://canonical-craft-application.readthedocs-hosted.com/en/latest/explanation/cryptography/
.. _umoci: https://umo.ci/
