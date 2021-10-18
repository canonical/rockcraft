#!/bin/bash -eux

venv_dir="$(mktemp -d)"

python3 -m venv "$venv_dir"
. "$venv_dir/bin/activate"

pip install git+https://github.com/canonical/craft-cli.git@616673f9312338c841e0da5de6417056aac88aa5#egg=craft_cli
pip install -e .
pip freeze --exclude-editable |grep -v ^craft-cli > requirements.txt
echo "git+https://github.com/canonical/craft-cli.git@616673f9312338c841e0da5de6417056aac88aa5#egg=craft_cli" >> requirements.txt

pip install -e .[dev]
pip freeze --exclude-editable | grep -v ^craft-cli > requirements-dev.txt
echo "git+https://github.com/canonical/craft-cli.git@616673f9312338c841e0da5de6417056aac88aa5#egg=craft_cli" >> requirements-dev.txt

rm -rf "$venv_dir"
