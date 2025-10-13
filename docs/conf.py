# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from pathlib import Path
import sys

SRC_DIR = Path(__file__).parent / ".."
SRC_DIR = SRC_DIR.resolve()
sys.path.insert(0, str(SRC_DIR))

project = 'purdy'
author = 'Christopher Trudeau'

import datetime
year = datetime.datetime.now().year
copyright = '%d-%d, %s' % (2019, year, author)

import purdy
version = purdy.__version__
release = version

nitpicky = False
nitpick_ignore = {
    ('py:class', 'Token'),
    ('py:class', 'rich.style.Style'),
    ('py:class', 'textual.widget.Widget'),
}

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinxarg.ext"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
