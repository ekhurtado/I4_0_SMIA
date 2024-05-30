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
release = '0.1.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # docString of the .py files
    # 'sphinx.ext.napoleon',  # To highlight some words
    'sphinx.ext.viewcode',  # To show the source code
    'sphinx.ext.autosectionlabel',  # It allows to refer sections its title (i.e. Parameters in docStrings).
    'sphinx.ext.autosummary',  # It generates function/method/attribute summary lists
    # 'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster' # default theme

html_static_path = ['_static']

# -----------------
# READTHEDOCS THEME
# ----------------
# html_theme = 'sphinx_rtd_theme'

# Add the CSS file to use all width of the webpage (for sphinx_rtd_theme)
# html_css_files = [
#     'css/custom.css',
# ]

# Configuration of sphinx_rtd_theme HTML theme
# html_theme_options = {
#     "navigation_depth": 2,
#     "collapse_navigation": False,
#     "logo_only": True
# }

# html_logo = 'images/Component_I4_0_logo_positive.png'   # To add the logo
# html_show_sphinx = False    # To not show “Created using Sphinx” in the HTML footer

# ---------
# FURO THEME
# ----------
# Documentation: https://pradyunsg.me/furo/customisation/fonts/
html_theme = 'furo'

# Configuration of Furo HTML theme
html_logo = "images/Component_I4_0_logo_positive.png"
html_theme_options = {
    # "light_logo": "images/Component_I4_0_logo_positive.png",
    # "dark_logo": "images/Component_I4_0_logo_positive.png",
    "light_css_variables": {
        "color-brand-primary": "#34A1E8",
        "color-brand-content": "#2980B9",
        "color-problematic": "blue",
        # "color-admonition-background": "#2980B9",
    },
}
pygments_dark_style = "monokai"

