# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys


sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'AAS Manager'
copyright = '2024, Ekaitz Hurtado'
author = 'Ekaitz Hurtado'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',   # docString of the .py files
    # 'sphinx.ext.napoleon',  # To highlight some words
    'sphinx.ext.viewcode',   # To show the source code
    'sphinx.ext.autosectionlabel',   # It allows to refer sections its title (i.e. Parameters in docStrings).
    'sphinx.ext.autosummary',   # It generates function/method/attribute summary lists
    # 'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'   # currently not working
# html_theme = " 'classic"
html_static_path = ['_static']
