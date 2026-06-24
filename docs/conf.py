"""Sphinx configuration for stockwell."""

import os
import sys
from datetime import datetime
from unittest.mock import MagicMock

# -- Path setup ----------------------------------------------------------

sys.path.insert(0, os.path.abspath('..'))

# -- Mock compiled C extensions for builds without FFTW3 -----------------

import ctypes  # noqa: E402
ctypes.CDLL = MagicMock()

# -- Project information -------------------------------------------------

project = 'stockwell'
copyright = '2021-2026, Claudio Satriano'
author = 'Claudio Satriano'

# The full version, including alpha/beta/rc tags.
from stockwell._version import get_versions  # noqa: E402
__version__ = get_versions()['version']
release = __version__
version = '.'.join(release.split('.')[:2])

# Release date in the format "Month DD, YYYY"
__release_date__ = get_versions()['date']
release_date = datetime.strptime(
    __release_date__, '%Y-%m-%dT%H:%M:%S%z'
).strftime('%b %d, %Y')
rst_epilog = f'\n.. |release date| replace:: {release_date}'

# -- General configuration -----------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinxcontrib.bibtex',
    'sphinx_mdinclude',
]

bibtex_bibfiles = ['refs.bib']
bibtex_reference_style = 'author_year'
bibtex_default_style = 'unsrt'

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
autodoc_typehints = 'description'
autosummary_generate = True

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output ---------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = [
    'custom.css',
]
