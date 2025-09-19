# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Graduate Admissions Analytics Dashboard'
copyright = '2025, Benjamin Lordi'
author = 'Benjamin Lordi'
release = '1.0'
version = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.viewcode',      # Adds source code links
    'sphinx.ext.napoleon',      # Support for Google/NumPy docstring styles
    'sphinx.ext.intersphinx',   # Link to other project documentation
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Project-specific configuration ------------------------------------------

# Add any Sphinx extension module names here, as strings
master_doc = 'index'

# The suffix(es) of source filenames
source_suffix = '.rst'

# The encoding of source files
source_encoding = 'utf-8-sig'

# Add any paths that contain custom static files (such as style sheets)
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names
html_sidebars = {
    '**': [
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}