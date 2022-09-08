*********
Tutorials
*********

Create a Hello World OCI image
==============================

Prerequisites
-------------

- snap enabled system https://snapcraft.io
- LXD installed
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
  summary: Hello World
  description: The most basic example of a ROCK.
  version: "1.0"
  base: ubuntu:20.04
  license: Apache-2.0
  cmd: [/usr/bin/hello, -t]
  platforms:
    amd64:  # Make sure this value matches your computer's architecture

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

  Launching instance...                                                                                                       
  Retrieved base ubuntu:20.04                                                                                                 
  Extracted ubuntu:20.04                                                                                                      
  Executed: pull hello                                                                                                        
  Executed: overlay hello                                                                                                     
  Executed: build hello                                                                                                       
  Executed: stage hello                                                                                                       
  Executed: prime hello                                                                                                       
  Executed parts lifecycle                                                                                                    
  Created new layer                                                                                                           
  Cmd set to ['/usr/bin/hello', '-t']                                                                                         
  Labels and annotations set to ['org.opencontainers.image.version=1.0', 'org.opencontainers.image.title=hello', 'org.opencontainers.image.ref.name=hello', 'org.opencontainers.image.licenses=Apache-2.0', 'org.opencontainers.image.created=2022-06-30T09:07:38.124741+00:00']                                                                                                        
  Exported to OCI archive 'hello_1.0_amd64.rock'  

At the end of the process, a file named ``hello_1.0_amd64.rock`` should be
present in the current directory.

Running OCI image in docker
---------------------------

First, import the recently created OCI Image into docker:

.. code-block:: sh

  skopeo --insecure-policy copy oci-archive:hello_1.0_amd64.rock docker-daemon:hello:1.0

Now run the ``hello`` command from the OCI image:

.. code-block:: sh

  $ docker run hello:1.0

Which should print:

.. code-block:: sh

  hello, world
