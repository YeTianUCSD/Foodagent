# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
from pathlib import Path

project = "CHA"
copyright = "2024, Mahyar Abbasian"
author = "Mahyar Abbasian"
doc_version = "version 0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    # "sphinxcontrib.autodoc_pydantic",
    "sphinx_copybutton",
    # "sphinx_panels",
    # "IPython.sphinxext.ipython_console_highlighting",
    "sphinxcontrib.video",
    "sphinxcontrib.youtube",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'furo' #'alabaster'
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_logo = "_static/logo.png"
html_css_files = [
    "custom.css",
]

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/Institute4FutureHealth/CHA",
            "icon": "fa-brands fa-github",
        },
    ],
    "secondary_sidebar_items": ["page-toc"],
    "logo": {
        "text": "open CHA",
        "image_light": "_static/logo-dark.png",
        "image_dark": "_static/logo.png",
    },
    # "navbar_start": ["navbar-logo"],
    # "navbar_end": ["theme-switcher", "navbar-icon-links"],
    # "navbar_persistent": ["search-button"],
    # "primary_sidebar_end": ["custom-template", "sidebar-ethical-ads"],
    # "article_footer_items": ["test", "test"],
    # "content_footer_items": ["test", "test"],
    "footer_start": ["copyright"],
    # "secondary_sidebar_items": ["page-toc"],  # Remove the source buttons
}

autodoc_default_options = {
    "private-members": True,
    "members": True,
    "exclude-members": "Config, model_config, model_fields",
}

# -- Path setup --------------------------------------------------------------

sys.path.append(str(Path(".").resolve()))
# sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../../"))
# sys.path.insert(0, os.path.abspath("../../interface"))
# sys.path.insert(0, os.path.abspath("/datapipes/memory"))
