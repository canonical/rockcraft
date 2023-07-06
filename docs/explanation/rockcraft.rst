.. _why_use_rockcraft:

Why use Rockcraft?
==================

Getting past the technical matters surrounding Rockcraft, from a higher
perspective, you might be asking *"but what is this after all?"* and *"why do
I need it?"*.

Let's then use this page to go a bit deeper into the concepts and definitions
behind Rockcraft.

So why do I need Rockcraft?
...........................

Now, this is where things get interesting. To answer this question, we first
need to look at the current state of the art with respect to the existing
container image offerings out there.

It is easy to find public studies (like `Unit 42 / Znet`_
and `Snyk's state of open source security report 2020`_) where the findings
state a concerning number of containers at risk deployed in cloud
infrastructures.

In fact, both these studies and our own assessments (dated from December 2021)
show that the most popular images in Docker Hub contain known vulnerabilities,
with Ubuntu being the only one without any critical or high ones.

.. image:: /_static/container-image-vulnerabilities.png
  :align: center
  :width: 95%
  :alt: Most popular container images contain known vulnerabilities

Sure, consumers could venture to fix these vulnerabilities themselves, but not
only would this increase the cost and proliferation of images, but it wouldn't
be easy to accomplish due to the lack of expertise in the subject matter. The
right approach is to actually fix the vulnerabilities at their source! And
Canonical has already started doing this. If we compare some of the Docker
Official container images vs some of the ones maintained by Canonical, we can
verify that the latter have no high/critical vulnerabilities in them!

.. image:: /_static/canonical-images-vulnerabilities.png
  :align: center
  :width: 95%
  :alt: vulnerabilities in Official vs Canonical-maintained OCI images

So this is where the motivation for a new generation of OCI images (aka ROCKs)
starts - the need for more secure container images! And while this need might
carry the biggest weight in the container users' demands, other values come into
play when selecting the best container image, such as:

* stability
* size
* compliance
* provenance

You can find these values and their relevance in `this report`_.

This brings us to the problem statement behind ROCKs:

    *How might we redesign secure container images \
    for Kubernetes developers and application maintainers, \
    considering the Top 10 Docker images \
    are full of vulnerabilities, except Ubuntu?*

A ROCK is:

* **secure** and **stable**: based on the latest and greatest Ubuntu releases;
* **OCI-compliant**: compatible with all the popular container management tools
  (Docker, Kubernetes, etc.);
* **dependable**: built on top of Ubuntu, with a predictable release cadence and
  timely security updates;
* **production-grade**: tested and secured by default.


Do I need to use Rockcraft?
---------------------------

If you want to build a proper ROCK, yes, we'd recommend you do. This is not to
say you wouldn't be able to build ROCK-like container images with your own
tools, but Rockcraft has been developed precisely to offer an easy way to build
production-grade container images.

Furthermore, Rockcraft is built on top of existing concepts and within the same
family as `Snapcraft <https://snapcraft.io/docs/snapcraft-overview>`_ and
`Charmcraft`_, such that its adoption becomes seamless for those already used
to building Snaps and Charms.


.. _Unit 42 / Znet: https://www.zdnet.com/article/96-of-third-party-container-applications-deployed-in-cloud-infrastructure-contain-known-vulnerabilities-unit-42/
.. _Snyk's state of open source security report 2020: https://snyk.io/blog/10-docker-image-security-best-practices/
.. _this report: https://juju.is/cloud-native-kubernetes-usage-report-2021#selection-criteria-for-container-images
