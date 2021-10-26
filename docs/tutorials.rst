*********
Tutorials
*********

Create a Hello World OCI image
==============================

Prerequisites
-------------

- snap enabled system https://snapcraft.io
- LXD setup on ext4
- skopeo installed https://github.com/containers/skopeo
- running docker setup
- a text editor


Installing Rockcraft
--------------------

Install Rockcraft on your host:

.. code-block:: sh
		
  $ snap install rockcraft --classic --edge

Project Setup
-------------

Create a new directory and write following into a a text editor and
save it as ``rockcraft.yaml``:

.. code-block:: yaml

  name: hello
  version: "1.0"
  base: ubuntu:20.04
  build-base: ubuntu:20.04

  parts:
      hello:
          plugin: nil
          overlay-packages:
              - hello

Create OCI image
----------------

Pack the OCI image, run:

.. code-block:: sh
		
  $ rockcraft pack


The output should look as follows:

.. code-block:: sh

  Retrieved base ubuntu:20.04                                                                                                   
  Extracted ubuntu:20.04                                                                                                        
  Executed parts lifecycle                                                                                                      
  Created new layer                                                                                                             
  Exported to OCI archive 'hello_1.0.rock'

At the end of the process, a file named ``hello_1.0.rock`` should be
present in the current directory.

Running OCI image in docker
---------------------------

First, import the recently created OCI Image into docker:

.. code-block:: sh

  skopeo --insecure-policy copy oci-archive:hello_1.0.rock docker-daemon:hello:1.0

Now run the ``hello`` command from the OCI image:

.. code-block:: sh

  $ docker run  --entrypoint /usr/bin/hello hello:1.0

Which should print:

.. code-block:: sh

  Hello, world!
