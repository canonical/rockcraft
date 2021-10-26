#!/bin/bash -eux

requirements_fixups() {
  req_file="$1"

  # Python apt library pinned to source.
  sed -i '/^python-apt==/d' "$req_file"

}

append_source_requirements() {
  req_file="$1"

  echo "git+https://github.com/canonical/craft-cli.git@6d770943c40defbeddb44c3b800a97b1b6595c01#egg=craft_cli" >> "$req_file"
  echo "git+https://github.com/canonical/craft-parts.git@778f45d796cb1f6677633cd161ddd32ef4d64c1b#egg=craft_parts" >> "$req_file"
  echo "git+https://github.com/canonical/craft-providers.git@de5b5f9c88f41b865634a3ac395e4b2db96f17e0#egg=craft_providers" >> "$req_file"
}

venv_dir="$(mktemp -d)"

python3 -m venv "$venv_dir"
. "$venv_dir/bin/activate"

# Pull in host python3-apt site package to avoid installation.
site_pkgs="$(readlink -f "$venv_dir"/lib/python3.*/site-packages/)"
temp_dir="$(mktemp -d)"
pushd "$temp_dir"
apt download python3-apt
dpkg -x ./*.deb .
cp -r usr/lib/python3/dist-packages/* "$site_pkgs"
popd

pip install git+https://github.com/canonical/craft-cli.git@6d770943c40defbeddb44c3b800a97b1b6595c01#egg=craft_cli
pip install git+https://github.com/canonical/craft-parts.git@778f45d796cb1f6677633cd161ddd32ef4d64c1b#egg=craft_parts
pip install git+https://github.com/canonical/craft-providers.git@de5b5f9c88f41b865634a3ac395e4b2db96f17e0#egg=craft_providers

pip install -e .[doc]
pip freeze --exclude-editable | egrep -v "^craft-(cli|parts|providers)" > requirements-doc.txt
requirements_fixups "requirements-doc.txt"

pip install -e .
pip freeze --exclude-editable | egrep -v "^craft-(cli|parts|providers)" > requirements.txt
requirements_fixups "requirements.txt"
append_source_requirements  "requirements.txt"

pip install -e .[dev]
pip freeze --exclude-editable | egrep -v "^craft-(cli|parts|providers)" > requirements-dev.txt
requirements_fixups "requirements-dev.txt"
append_source_requirements  "requirements-dev.txt"

rm -rf "$venv_dir"
