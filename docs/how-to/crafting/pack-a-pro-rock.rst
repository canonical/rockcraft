.. meta::
    :description: Pack a rock that contains extended security patches or meets regulatory compliance needs, powered by Ubuntu Pro.

.. _how-to-pack-a-pro-rock:

Pack a Pro-compliant rock
=========================

Follow this guide to pack a rock that contains extended security patches or meets
regulatory compliance needs.

Prerequisites
-------------

- An Ubuntu Pro system (https://ubuntu.com/pro)
- LXD installer (https://documentation.ubuntu.com/lxd/)
- Rockcraft version 1.18.0 or higher installed (https://snapcraft.io/rockcraft)

Enable guest attachment
-----------------------

Rockcraft makes use of Ubuntu Pro’s own support for LXD instances, but this support needs
to be explicitly enabled and configured. On a terminal, run:

.. terminal::

    sudo pro config set lxd_guest_attach=available

This command lets Rockcraft attach its LXD instances to the system’s Pro subscription,
and only needs to be executed once.

Next, restart LXD so that the new configuration takes effect:

.. terminal::

    sudo snap restart lxd

Identify the required Pro services
----------------------------------

Next, determine which Pro services fit your needs. Rockcraft supports the following services:

- ``esm-apps`` or ``esm-infra``: If your goal is to pack a rock for an application and include
  the latest security patches for a base that is no longer under Standard Security Maintenance.
- ``fips``, ``fips-updates`` or ``fips-preview``: If you need to deploy your rock in a highly
  regulated environment that processes sensitive data.

The desired Pro services don’t need to be enabled on your system, but they do need to be
available. Run ``pro status`` and check the ``ENTITLED`` column to check whether a service is
available. The Ubuntu Pro Client documentation has
`further information <https://documentation.ubuntu.com/pro-client/en/v32/explanations/which_services/>`_
on each service.

Pack the rock
-------------

Now you can pack the rock with the desired services. Provide them to the ``--pro`` option:

.. terminal::

    rockcraft pack --pro=<service>

To use multiple services, pass them to the option as comma-separated values. For example,
to pack a rock with the ``esm-apps`` and ``esm-infra`` services call:

.. terminal::

    rockcraft pack --pro=esm-apps,esm-infra

Rockcraft will automatically attach the Pro subscription and enable the requested services on
the LXD instance while packing the rock.
