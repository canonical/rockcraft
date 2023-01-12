DOCSVENV = docs/env/bin/activate
PORT = 8080

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

.PHONY: docs
docs: ## Generate documentation.
	rm -f docs/rockcraft.rst
	rm -f docs/modules.rst
	. $(DOCSVENV); $(MAKE) -C docs clean
	. $(DOCSVENV); $(MAKE) -C docs html

.PHONY: rundocs
rundocs: ## start a documentation runserver
	. $(DOCSVENV); sphinx-autobuild $(ALLSPHINXOPTS) --ignore ".git/*" --ignore "*.scss" ./docs -b dirhtml -a docs/_build/html --host 0.0.0.0 --port $(PORT)


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
lint: test-black test-codespell test-flake8 test-isort test-mypy test-pydocstyle test-pyright test-pylint test-sphinx-lint ## Run all linting tests.

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

.PHONY: test-sphinx-lint
test-sphinx-lint:
	sphinx-lint --ignore docs/_build --max-line-length 80 -e all docs/*

.PHONY: test-units
test-units: ## Run unit tests.
	pytest tests/unit

.PHONY: tests
tests: lint test-integrations test-units ## Run all tests.
