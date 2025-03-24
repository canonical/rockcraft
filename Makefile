<<<<<<< HEAD
PROJECT=rockcraft

ifneq ($(wildcard /etc/os-release),)
include /etc/os-release
export
endif

ifneq ($(VERSION_CODENAME),)
SETUP_TESTS_EXTRA_ARGS=--extra apt-$(VERSION_CODENAME)
endif

UV_FROZEN=true
=======
PROJECT=starcraft
UV_TEST_GROUPS := "--group=dev"
UV_DOCS_GROUPS := "--group=docs"
UV_LINT_GROUPS := "--group=lint" "--group=types"

# If you have dev dependencies that depend on your distro version, uncomment these:
# ifneq ($(wildcard /etc/os-release),)
# include /etc/os-release
# endif
# ifdef VERSION_CODENAME
# UV_TEST_GROUPS += "--group=dev-$(VERSION_CODENAME)"
# UV_DOCS_GROUPS += "--group=dev-$(VERSION_CODENAME)"
# UV_LINT_GROUPS += "--group=dev-$(VERSION_CODENAME)"
# endif
>>>>>>> starbase/main

include common.mk

.PHONY: format
format: format-ruff format-codespell format-prettier  ## Run all automatic formatters

.PHONY: lint
lint: lint-ruff lint-codespell lint-mypy lint-prettier lint-pyright lint-shellcheck lint-docs lint-twine  ## Run all linters

.PHONY: pack
<<<<<<< HEAD
pack: pack-pip pack-snap  ## Build all packages
=======
pack: pack-pip  ## Build all packages
>>>>>>> starbase/main

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

<<<<<<< HEAD
.PHONY: setup
setup: install-uv setup-precommit ## Set up a development environment
	uv sync --frozen $(SETUP_TESTS_EXTRA_ARGS) --extra docs --extra lint --extra types

# Used for installing build dependencies in CI.
.PHONY: install-build-deps
install-build-deps: install-linux-build-deps install-lint-build-deps
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
	sudo $(APT) install libyaml-dev python3-dev python3-pip python3-setuptools \
	  python3-venv python3-wheel fuse-overlayfs libapt-pkg-dev umoci libgit2-dev
endif
ifneq ($(shell which snap),)
	sudo snap install lxd
endif
ifneq ($(shell which lxd),)
	sudo lxd init --auto
endif
=======
# Find dependencies that need installing
APT_PACKAGES :=
ifeq ($(wildcard /usr/include/libxml2/libxml/xpath.h),)
APT_PACKAGES += libxml2-dev
endif
ifeq ($(wildcard /usr/include/libxslt/xslt.h),)
APT_PACKAGES += libxslt1-dev
endif
ifeq ($(wildcard /usr/share/doc/python3-venv/copyright),)
APT_PACKAGES += python3-venv
endif

# Used for installing build dependencies in CI.
.PHONY: install-build-deps
install-build-deps: install-lint-build-deps
ifeq ($(APT_PACKAGES),)
else ifeq ($(shell which apt-get),)
	$(warning Cannot install build dependencies without apt.)
	$(warning Please ensure the equivalents to these packages are installed: $(APT_PACKAGES))
else
	sudo $(APT) install $(APT_PACKAGES)
endif

# If additional build dependencies need installing in order to build the linting env.
.PHONY: install-lint-build-deps
install-lint-build-deps:
>>>>>>> starbase/main
