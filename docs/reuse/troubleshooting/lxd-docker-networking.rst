.. warning::

   There is a `known connectivity issue with LXD and Docker
   <https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker>`_. If we see a
   networking issue such as "*A network related operation failed in a context of no
   network access*" or ``Client.Timeout``, we need to allow egress network traffic
   to flow from the managed LXD bridge.

   First, list the available networks:

   .. code-block:: bash

      lxc network list

   The bridge will have ``TYPE: bridge`` and ``MANAGED: YES``. Save its name to an
   environment variable:

   .. code-block:: bash

      NETWORK_BRIDGE=<name of managed LXD bridge>

   Then update the network traffic flow:

   .. code-block:: bash

      sudo iptables  -I DOCKER-USER -i $NETWORK_BRIDGE -j ACCEPT
      sudo ip6tables -I DOCKER-USER -i $NETWORK_BRIDGE -j ACCEPT
      sudo iptables  -I DOCKER-USER -o $NETWORK_BRIDGE -m conntrack \
        --ctstate RELATED,ESTABLISHED -j ACCEPT
      sudo ip6tables -I DOCKER-USER -o $NETWORK_BRIDGE -m conntrack \
        --ctstate RELATED,ESTABLISHED -j ACCEPT
