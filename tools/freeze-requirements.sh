#!/bin/bash -eux

requirements_fixups() {
  req_file="$1"

  # Python apt library pinned to source.
  sed -i '/^python-apt==/d' "$req_file"
}


uv pip compile --upgrade --output-file requirements.txt pyproject.toml
requirements_fixups "requirements.txt"

uv pip compile --upgrade --extra doc --output-file requirements-doc.txt pyproject.toml
requirements_fixups "requirements-doc.txt"
