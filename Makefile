.PHONY: help
help: ## Show this help.
	@printf "%-40s %s\n" "Target" "Description"
	@printf "%-40s %s\n" "------" "-----------"
	@fgrep " ## " $(MAKEFILE_LIST) | fgrep -v grep | awk -F ': .*## ' '{$$1 = sprintf("%-40s", $$1)} 1'

.PHONY: autoformat
autoformat: ## Run automatic code formatters.
	isort .
	autoflake rockcraft/ tests/
	black .
	ruff check --fix-only rockcraft tests

.PHONY: clean
clean: ## Clean artifacts from building, testing, etc.
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +
	rm -rf docs/_build/
	rm -f docs/rockcraft.*
	rm -f docs/modules.rst
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache

.PHONY: coverage
coverage: ## Run pytest with coverage report.
	coverage run --source craft_sore -m pytest
	coverage report -m
	coverage html

.PHONY: preparedocs
preparedocs: ## mv file for docs
	cp sphinx-starter-pack/.sphinx/_static/* docs/_static
	mkdir docs/_templates
	cp sphinx-starter-pack/.sphinx/_templates/* docs/_templates
	cp sphinx-starter-pack/.sphinx/spellingcheck.yaml docs/spellingcheck.yaml

.PHONY: installdocs
installdocs: ## install documentation dependencies.
	$(MAKE) -C docs install

.PHONY: docs
docs: ## Generate documentation.
	rm -f docs/rockcraft.rst
	rm -f docs/modules.rst
	$(MAKE) -C docs clean-doc
	$(MAKE) -C docs html

.PHONY: rundocs
rundocs: ## start a documentation runserver
	$(MAKE) -C docs run

.PHONY: dist
dist: clean ## Build python package.
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

.PHONY: freeze-requirements
freeze-requirements:  ## Re-freeze requirements.
	tools/freeze-requirements.sh

.PHONY: install
install: clean ## Install python package.
	python setup.py install

.PHONY: lint
lint: test-black test-codespell test-flake8 test-isort test-mypy test-pydocstyle test-pyright test-pylint test-sphinx-lint test-shellcheck ## Run all linting tests.

.PHONY: release
release: dist ## Release with twine.
	twine upload dist/*

.PHONY: test-black
test-black:
	black --check --diff .

.PHONY: test-codespell
test-codespell:
	codespell .

.PHONY: test-flake8
test-flake8:
	flake8 rockcraft tests

.PHONY: test-ruff
test-ruff:
	ruff rockcraft tests

.PHONY: test-integrations
test-integrations: ## Run integration tests.
	pytest tests/integration

.PHONY: test-isort
test-isort:
	isort --check rockcraft tests

.PHONY: test-mypy
test-mypy:
	mypy rockcraft tests

.PHONY: test-pydocstyle
test-pydocstyle:
	pydocstyle rockcraft

.PHONY: test-pylint
test-pylint:
	pylint rockcraft
	pylint tests --disable=invalid-name,missing-module-docstring,missing-function-docstring,redefined-outer-name,too-many-arguments,too-many-public-methods

.PHONY: test-pyright
test-pyright:
	pyright .

.PHONY: test-shellcheck
test-shellcheck:
	# shellcheck for shell scripts
	git ls-files | file --mime-type -Nnf- | grep shellscript | cut -f1 -d: | xargs shellcheck
	# shellcheck for bash commands inside spread task.yaml files
	tools/external/utils/spread-shellcheck tests/spread/ spread.yaml

.PHONY: test-sphinx-lint
test-sphinx-lint:
	sphinx-lint --ignore docs/_build --ignore docs/env --max-line-length 80 -e all docs/*

.PHONY: test-units
test-units: ## Run unit tests.
	pytest tests/unit

.PHONY: tests
tests: lint test-integrations test-units ## Run all tests.
	$(MAKE) -C docs linkcheck
	$(MAKE) -C docs woke
	$(MAKE) -C docs spelling