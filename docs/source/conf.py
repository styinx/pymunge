from pathlib import Path
import sys


ROOT_DIR = Path(__file__).parent.parent.parent.resolve()
SOURCE_DIR = ROOT_DIR / 'source'
PYMUNGE_DIR = SOURCE_DIR / 'pymunge'


# Add source directory
sys.path.append(str(SOURCE_DIR))
sys.path.append(str(PYMUNGE_DIR))


from version import MAJOR, MINOR


# Project
project = 'pymunge'
copyright = '2025, styinx'
author = 'styinx'
release = f'{MAJOR}.{MINOR}'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc'
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = 'furo'
html_theme_options = {
}
