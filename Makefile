PROJECT=rockcraft
# Define when more than the main package tree requires coverage
# like is the case for snapcraft (snapcraft and snapcraft_legacy):
# COVERAGE_SOURCE="starcraft"
UV_TEST_GROUPS := "--group=dev"
UV_DOCS_GROUPS := "--group=docs"
UV_LINT_GROUPS := "--group=lint" "--group=types"
UV_TICS_GROUPS := "--group=tics"

# If you have dev dependencies that depend on your distro version, uncomment these:
ifneq ($(wildcard /etc/os-release),)
include /etc/os-release
endif
ifdef VERSION_CODENAME
UV_TEST_GROUPS += "--group=dev-$(VERSION_CODENAME)"
UV_DOCS_GROUPS += "--group=dev-$(VERSION_CODENAME)"
UV_LINT_GROUPS += "--group=dev-$(VERSION_CODENAME)"
UV_TICS_GROUPS += "--group=dev-$(VERSION_CODENAME)"
endif

include common.mk

.PHONY: format
format: format-ruff format-codespell format-prettier format-pre-commit  ## Run all automatic formatters

.PHONY: lint
lint: lint-ruff lint-codespell lint-mypy lint-prettier lint-pyright lint-shellcheck lint-docs lint-twine lint-uv-lockfile  ## Run all linters

.PHONY: pack
pack: pack-pip pack-snap  ## Build all packages

.PHONY: pack-snap
pack-snap: snap/snapcraft.yaml  ##- Build snap package
ifeq ($(shell which snapcraft),)
	sudo snap install --classic snapcraft
endif
	snapcraft pack

schema: install-uv  ## Generate the schema file.
	mkdir -p schema
	uv run python tools/schema/schema.py > schema/rockcraft.json

validate-schema: install-ajv-cli
	# Find all the rockcraft.yaml files that don't contain "# pragma: no-schema-validate"
	find . -type f -name rockcraft.yaml -exec grep -HL '# pragma: no-schema-validate' '{}' '+' | \
	xargs -I {} ajv validate --strict=false --spec=draft2020 -s schema/rockcraft.json -d {}
    # The line below can be used to use the go-based jv command instead.
    # xargs -I {} sh -c 'echo "\e[32mValidating {}\e[0m"; jv schema/rockcraft.json {}'

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
ifeq ($(wildcard /usr/share/doc/libyaml-dev/copyright),)
APT_PACKAGES += libyaml-dev
endif
ifeq ($(wildcard /usr/share/doc/fuse-overlayfs/copyright),)
APT_PACKAGES += fuse-overlayfs
endif
ifeq ($(wildcard /usr/share/doc/umoci/copyright),)
APT_PACKAGES += umoci
endif
ifeq ($(wildcard /usr/share/doc/skopeo/copyright),)
APT_PACKAGES += skopeo
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


.PHONY: install-ajv-cli
install-ajv-cli: install-npm
ifneq ($(shell which ajv),)
else
	npm install -g ajv-cli
endif
