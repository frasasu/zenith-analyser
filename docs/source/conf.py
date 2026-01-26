# -*- coding: utf-8 -*-
#
# Zenith Analyser documentation build configuration file
# Copyright 2026 François TUMUSAVYEYESU
# Licensed under Apache License 2.0

import os
import sys

# Add the source code path so Sphinx can find the modules
sys.path.insert(0, os.path.abspath('../../src'))

project = 'Zenith Analyser'
copyright = '2026, François TUMUSAVYEYESU'
author = 'François TUMUSAVYEYESU'

# The full version, including alpha/beta/rc tags
release = '0.1.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',          # Support for Google/NumPy style docstrings
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Make signatures nicer
autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'private-members': False,
    'special-members': False,
}

# Napoleon settings (for nice docstring rendering)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True