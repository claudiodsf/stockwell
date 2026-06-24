# Minimal makefile for Sphinx documentation
#
# Uses the 'sphinx' conda environment for the build.

SPHINXOPTS    ?=
SPHINXBUILD   ?= conda run -n sphinx sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
