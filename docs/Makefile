# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -q
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
VENV          = env/bin/activate
PORT = 8080

# Locate this directory relative to the repository root. See woke recipe.
REPOROOT = $(shell git rev-parse --show-toplevel)
RELCWD = $(shell realpath --relative-to=$(REPOROOT) $(CURDIR))

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

install:
	@echo "... setting up virtualenv"
	python3 -m venv env
	. $(VENV); pip install --upgrade -r ../requirements-doc.txt -r ../requirements-jammy.txt

run:
	. $(VENV); sphinx-autobuild --ignore ".git/*" --ignore "*.scss"  -c . -b dirhtml "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) --host 0.0.0.0 --port $(PORT)

html:
	. $(VENV); $(SPHINXBUILD) -c . -b dirhtml "$(SOURCEDIR)" "$(BUILDDIR)" -w warnings.txt $(SPHINXOPTS) $(O)

clean: clean-doc
	rm -rf env

clean-doc:
	rm -rf "$(BUILDDIR)"

spelling: html
	. $(VENV) ; python -m pyspelling -c spellingcheck.yaml

linkcheck:
	. $(VENV) ; $(SPHINXBUILD) -c . -b linkcheck  "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

woke:
	type woke >/dev/null 2>&1 || { snap install woke; exit 1; }

	# Woke appears to have a issue where it skips .*ignore files unless it is executed from the repo root.
	# This is mitigated by changing to the repo root and running woke on the relative docs path.
	# Tested on 19/07/24 with woke 0.19.0-4-g5d52c15
	cd ..; woke $(RELCWD)/**/*.rst $(RELCWD)/*.rst \
		-c https://github.com/canonical-web-and-design/Inclusive-naming/raw/main/config.yml \
		--disable-default-rules \
		--exit-1-on-failure

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	. $(VENV); $(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
