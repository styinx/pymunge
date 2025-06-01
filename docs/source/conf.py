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

extensions = [
    'sphinx.ext.autodoc'
]

templates_path = ['_templates']
exclude_patterns = []
numfig = True

# HTML
html_css_files = ['custom.css']
html_static_path = ['_static']
html_theme = 'furo'
html_theme_options = {}
html_favicon = '_static/pymunge.ico'
html_logo= '_static/pymunge.png'

