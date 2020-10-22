# -*- coding: utf-8 -*-
#
# complexity documentation build configuration file, created by
# sphinx-quickstart on Tue Jul  9 22:26:36 2013.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import datetime
import os
import sys

import jupyter_forward

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))

cwd = os.getcwd()
parent = os.path.dirname(cwd)
sys.path.insert(0, parent)


# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'IPython.sphinxext.ipython_console_highlighting',
    'IPython.sphinxext.ipython_directive',
    'sphinx.ext.napoleon',
    'myst_parser',
]

autodoc_member_order = 'groupwise'

myst_amsmath_enable = True
myst_admonition_enable = True
myst_html_img_enable = True
myst_dmath_enable = True
myst_deflist_enable = True
myst_figure_enable = True
myst_url_schemes = ('http', 'https', 'mailto')
myst_heading_anchors = 2
panels_add_boostrap_css = False

extlinks = {
    'issue': ('https://github.com/intake/jupyter-forward/issues/%s', 'GH#'),
    'pr': ('https://github.com/intake/jupyter-forward/pull/%s', 'GH#'),
}
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Autosummary pages will be generated by sphinx-autogen instead of sphinx-build
autosummary_generate = []

# Otherwise, the Return parameter list looks different from the Parameters list
napoleon_use_rtype = False


# Enable notebook execution
# https://nbsphinx.readthedocs.io/en/0.4.2/never-execute.html
# nbsphinx_execute = 'auto'
# Allow errors in all notebooks by
# nbsphinx_allow_errors = True

# # Disable cell timeout
# nbsphinx_timeout = -1


# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
current_year = datetime.datetime.now().year
project = u'jupyter-forward'
copyright = f'2018-{current_year}, the jupyter-forward development team'
author = u'jupyter-forward developers'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = jupyter_forward.__version__.split('+')[0]
# The full version, including alpha/beta/rc tags.
release = jupyter_forward.__version__


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', '**.ipynb_checkpoints', 'Thumbs.db', '.DS_Store']


# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'pydata_sphinx_theme'


# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = 'images/NSF_4-Color_bitmap_Logo.png'
html_context = {
    'github_user': 'intake',
    'github_repo': 'jupyter-forward',
    'github_version': 'master',
    'doc_path': 'docs',
}
html_theme_options = {
    'github_url': 'https://github.com/NCAR/jupyter-forward',
    'twitter_url': 'https://twitter.com/NCARXDev',
    'show_toc_level': 1,
}


# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_build/html/_static']

# Sometimes the savefig directory doesn't exist and needs to be created
# https://github.com/ipython/ipython/issues/8733
# becomes obsolete when we can pin ipython>=5.2; see ci/requirements/doc.yml
# ipython_savefig_dir = os.path.join(
#     os.path.dirname(os.path.abspath(__file__)), '_build', 'html', '_static'
# )

# savefig_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'source', '_static')

# os.makedirs(ipython_savefig_dir, exist_ok=True)
# os.makedirs(savefig_dir, exist_ok=True)

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'


# Output file base name for HTML help builder.
htmlhelp_basename = 'jupyter_forwarddoc'


# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
}


latex_documents = [
    ('index', 'jupyter-forward.tex', u'jupyter-forward Documentation', author, 'manual')
]

man_pages = [('index', 'jupyter-forward', u'jupyter-forward Documentation', [author], 1)]

texinfo_documents = [
    (
        'index',
        'jupyter-forward',
        u'jupyter-forward Documentation',
        author,
        'jupyter-forward',
        'One line description of project.',
        'Miscellaneous',
    )
]

ipython_warning_is_error = False
ipython_execlines = []


intersphinx_mapping = {}
