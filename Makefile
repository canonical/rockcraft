.PHONY: help
help: ## Show this help.
	@printf "%-40s %s\n" "Target" "Description"
	@printf "%-40s %s\n" "------" "-----------"
	@fgrep " ## " $(MAKEFILE_LIST) | fgrep -v grep | awk -F ': .*## ' '{$$1 = sprintf("%-40s", $$1)} 1'

.PHONY: autoformat
autoformat: ## Run automatic code formatters.
	autoflake rockcraft/ tests/
	black .
	ruff check --fix-only rockcraft tests

.PHONY: clean
clean: ## Clean artefacts from building, testing, etc.
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +
	rm -rf docs/_build/
	rm -f docs/rockcraft.*
	rm -f docs/modules.rst
	rm -rf docs/reference/commands
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache
	$(MAKE) -C docs clean
	rm -rf .mypy_cache

.PHONY: coverage
coverage: ## Run pytest with coverage report.
	coverage run --source rockcraft -m pytest tests/unit
	coverage report -m
	coverage html
	coverage xml -o results/coverage-unit.xml

.PHONY: installdocs
installdocs:
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
lint: test-black test-codespell test-flake8 test-mypy test-pydocstyle test-pyright test-ruff test-sphinx-lint test-shellcheck ## Run all linting tests.

.PHONY: release
release: dist ## Release with twine.
	twine upload dist/*

.PHONY: test-black
test-black:
	black --check --diff .

.PHONY: test-codespell
test-codespell:
	codespell rockcraft tests

.PHONY: test-flake8
test-flake8:
	flake8 rockcraft tests

.PHONY: test-ruff
test-ruff:
	ruff check rockcraft tests

.PHONY: test-integrations
test-integrations: ## Run integration tests.
	pytest tests/integration

.PHONY: test-mypy
test-mypy:
	mypy rockcraft tests

.PHONY: test-pydocstyle
test-pydocstyle:
	pydocstyle rockcraft

.PHONY: test-pylint
test-pylint:
	echo "rockcraft has replaced pylint with ruff. Please use `make test-ruff` instead."
	make test-ruff

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
	sphinx-lint --ignore docs/sphinx-starter-pack/ --ignore docs/_build --ignore docs/env --max-line-length 80 -e all docs/*

.PHONY: test-units
test-units: ## Run unit tests.
	pytest tests/unit

.PHONY: test-docs
test-docs: installdocs ## Run docs tests.
	$(MAKE) -C docs linkcheck
	$(MAKE) -C docs woke
	$(MAKE) -C docs spelling

.PHONY: tests
tests: lint test-integrations test-units test-docs ## Run all tests.
