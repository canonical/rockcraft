PROJECT=rockcraft

ifneq ($(wildcard /etc/os-release),)
include /etc/os-release
export
endif

ifneq ($(VERSION_CODENAME),)
SETUP_TESTS_EXTRA_ARGS=--extra apt-$(VERSION_CODENAME)
endif

UV_FROZEN=true

include common.mk

.PHONY: format
format: format-ruff format-codespell  ## Run all automatic formatters

.PHONY: lint
lint: lint-ruff lint-codespell lint-mypy lint-pyright lint-shellcheck lint-yaml lint-docs lint-twine  ## Run all linters

.PHONY: pack
pack: pack-pip pack-snap  ## Build all packages

.PHONY: pack-snap
pack-snap: snap/snapcraft.yaml  ##- Build snap package
ifeq ($(shell which snapcraft),)
	sudo snap install --classic snapcraft
endif
	snapcraft pack

.PHONY: publish
publish: publish-pypi  ## Publish packages

.PHONY: publish-pypi
publish-pypi: clean package-pip lint-twine  ##- Publish Python packages to pypi
	uv tool run twine upload dist/*

.PHONY: setup
setup: install-uv setup-precommit ## Set up a development environment
	uv sync --frozen $(SETUP_TESTS_EXTRA_ARGS) --extra docs --extra lint --extra types

# Used for installing build dependencies in CI.
.PHONY: install-build-deps
install-build-deps: install-linux-build-deps install-macos-build-deps install-lint-build-deps
	# Ensure the system pip is new enough. If we get an error about breaking system packages, it is.
	sudo pip install 'pip>=22.2' || true

.PHONY: install-lint-build-deps
install-lint-build-deps:
ifeq ($(shell which apt-get),)
	$(warning apt-get not found. Please install lint dependencies yourself.)
else
	sudo $(APT) install python-apt-dev libapt-pkg-dev clang
endif

.PHONY: install-linux-build-deps
install-linux-build-deps:
ifneq ($(OS),Linux)
else ifeq ($(shell which apt-get),)
	$(warning apt-get not found. Please install dependencies yourself.)
else
	sudo $(APT) install skopeo
	# Needed for integration testing the charm plugin.
	sudo $(APT) install libyaml-dev python3-dev python3-pip python3-setuptools python3-venv python3-wheel
endif
ifneq ($(shell which snap),)
	sudo snap install lxd
endif
ifneq ($(shell which lxd),)
	sudo lxd init --auto
endif
