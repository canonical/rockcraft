#!/bin/bash -eux

venv_dir="$(mktemp -d)"

python3 -m venv "$venv_dir"
. "$venv_dir/bin/activate"

pip install -e .
pip freeze --exclude-editable > requirements.txt

pip install -e .[dev]
pip freeze --exclude-editable > requirements-dev.txt

rm -rf "$venv_dir"
