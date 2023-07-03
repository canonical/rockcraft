#!/bin/bash

ln -fs $(python3 -c 'import os, craft_parts_docs;print(os.path.split(craft_parts_docs.__file__)[0])') docs/common/craft-parts
