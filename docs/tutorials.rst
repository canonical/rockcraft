*********
Tutorials
*********


Create a Hello World ROCK
=========================

Prerequisites
-------------

- snap enabled system https://snapcraft.io
- LXD installed
- skopeo installed https://github.com/containers/skopeo
- Docker installed (https://docs.docker.com/get-docker/)
- a text editor


Install Rockcraft
-----------------

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

Pack the ROCK with Rockcraft
----------------------------

To build the ROCK, run:

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
present in the current directory. That's your ROCK, in oci-archive format.


Run the ROCK in Docker
----------------------

First, import the recently created ROCK into Docker:

.. code-block:: sh

  skopeo --insecure-policy copy oci-archive:hello_1.0_amd64.rock docker-daemon:hello:1.0

Now run the ``hello`` command from the ROCK:

.. code-block:: sh

  $ docker run hello:1.0

Which should print:

.. code-block:: sh

  hello, world


Publish a ROCK to a registry
============================

Prerequisites
-------------

- skopeo installed https://github.com/containers/skopeo
- Docker installed (https://docs.docker.com/get-docker/)


Push a ROCK to Docker Hub
-------------------------

The output of ``rockcraft pack`` is a ROCK in its oci-archive archive format. For the sake of this tutorial, 
let's say that this file's name is "myrock_1.0_amd64.rock", and that you want to push it to Docker Hub, 
as "tutorials/myrock:1.0":

.. code-block:: sh

  $ skopeo --insecure-policy copy --multi-arch all oci-archive:myrock_1.0_amd64.rock docker://tutorials/myrock:1.0
  Getting image source signatures
  Copying blob e65b2e587073 skipped: already exists  
  Copying blob 01f981dde5a5 skipped: already exists  
  Copying config 5da22a9016 done  
  Writing manifest to image destination
  Storing signatures

