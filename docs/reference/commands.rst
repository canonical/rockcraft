
******************
Rockcraft commands
******************

Lifecycle commands
..................
Lifecycle commands can take an optional parameter ``<part-name>``. When a part
name is provided, the command applies to the specific part. When no part name is
provided, the command applies to all parts.

clean
^^^^^
Removes a part's assets. When no part is provided, the entire build environment
(e.g. the LXD instance) is removed.

pull
^^^^
Downloads or retrieves artifacts defined for each part.

overlay
^^^^^^^
Execute operations defined for each part on a layer over the base filesystem,
potentially modifying its contents.

build
^^^^^
Builds artifacts defined for each part.

stage
^^^^^
Stages built artifacts into a common staging area, for each part.

prime
^^^^^
Prepare, for each part, the final payload to be packed as a ROCK, performing
additional processing and adding metadata files.

pack
^^^^
*This is the default lifecycle command for* ``rockcraft``.

Process parts and create the ROCK as an OCI archive file containing the project
payload with the provided metadata.

Other commands
..............
init
^^^^
Initializes a rockcraft project with a boilerplate ``rockcraft.yaml`` file.

help
^^^^
Shows information about a command.

