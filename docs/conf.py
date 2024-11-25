# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'I4.0 SMIA'
copyright = '2024, Ekaitz Hurtado'
author = 'Ekaitz Hurtado'
release = '0.2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # docString of the .py files
    'sphinx.ext.napoleon',  # To highlight some words
    'sphinx.ext.viewcode',  # To show the source code
    'sphinx.ext.autosectionlabel',  # It allows to refer sections its title (i.e. Parameters in docStrings).
    'sphinx.ext.autosummary',  # It generates function/method/attribute summary lists
    # 'sphinx_rtd_theme',
    'sphinx_inline_tabs',   # Add inline tabbed content to your Sphinx documentation (.. tab::)
    'sphinx_copybutton',
    'notfound.extension',
    'sphinx_design',
    'sphinxcontrib.youtube'
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
#
# # Add the CSS file to use all width of the webpage (for sphinx_rtd_theme)
# html_css_files = [
#     'css/custom.css',
# ]
#
# # Configuration of sphinx_rtd_theme HTML theme
# html_theme_options = {
#     "navigation_depth": 2,
#     "collapse_navigation": False,
#     "logo_only": True
# }
#
# html_logo = 'images/Component_I4_0_logo_positive.png'   # To add the logo
# html_show_sphinx = False    # To not show “Created using Sphinx” in the HTML footer

# ----------
# FURO THEME
# ----------
# Documentation: https://pradyunsg.me/furo/customisation/fonts/
html_theme = 'furo'

# Configuration of Furo HTML theme
# All color definitions: https://github.com/pradyunsg/furo/blob/main/src/furo/assets/styles/variables/_colors.scss
html_logo = "_static/images/I4_0_SMIA_logo_rtd.png"
html_favicon = "_static/images/I4_0_SMIA_favicon.svg"

html_theme_options = {
    # "light_logo": "images/Component_I4_0_logo_positive.png",
    # "dark_logo": "images/Component_I4_0_logo_positive.png",
    "light_css_variables": {
        "color-brand-primary": "#34A1E8",
        "color-brand-content": "#2980B9",
        "color-problematic": "DodgerBlue",  # other CSS colors: https://www.w3schools.com/cssref/css_colors.php
        # "color-admonition-background": "#2980B9",
        "color-api-background": "#E7F2FA",
        "color-api-background-hover": "#b7c0c6",
    },
    "dark_css_variables": {  # colors for dark theme
        "color-brand-primary": "#34A1E8",
        "color-brand-content": "#2980B9",
        "color-problematic": "DodgerBlue",
        "color-api-background": "#383838",
        "color-api-background-hover": "#5e5e5e",
    }
}

pygments_dark_style = "monokai"

html_show_sphinx = False    # To not show “Created using Sphinx” in the HTML footer

autodoc_member_order = 'bysource'   # To not sort Sphinx output in alphabetical order (API documentation)

