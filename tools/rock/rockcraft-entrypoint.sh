#!/bin/bash -ex

apt update &>/dev/null

export PATH="$PATH:/usr/libexec/rockcraft"

rsync -a --exclude="*.rock" /project/ /workdir

/usr/libexec/rockcraft/rockcraft pack --destructive-mode "$@"

(ls /workdir/*.rock &>/dev/null && cp /workdir/*.rock /project/) || \
    echo "No rocks were built. Exiting..."
