#!/bin/bash -eux

requirements_fixups() {
  req_file="$1"

  # Python apt library pinned to source.
  sed -i '/^python-apt==/d' "$req_file"
}


venv_dir="$(mktemp -d)"

python3 -m venv "$venv_dir"

# shellcheck disable=SC1090,SC1091 # don't follow sources
. "$venv_dir/bin/activate"
pip install pip-tools

# Pull in host python3-apt site package to avoid installation.
site_pkgs="$(readlink -f "$venv_dir"/lib/python3.*/site-packages/)"
temp_dir="$(mktemp -d)"
pushd "$temp_dir"
apt download python3-apt
dpkg -x ./*.deb .
cp -r usr/lib/python3/dist-packages/* "$site_pkgs"
popd

pip-compile --upgrade --output-file requirements.txt
requirements_fixups "requirements.txt"

pip-compile --upgrade --extra doc --output-file requirements-doc.txt
requirements_fixups "requirements-doc.txt"

pip-compile --upgrade --extra dev --output-file requirements-dev.txt
requirements_fixups "requirements-dev.txt"

rm -rf "$venv_dir"
