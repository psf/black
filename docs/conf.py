#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/stable/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import re
import string
from importlib.metadata import version
from pathlib import Path

from sphinx.application import Sphinx

CURRENT_DIR = Path(__file__).parent


def make_pypi_svg(version: str) -> None:
    template: Path = CURRENT_DIR / "_static" / "pypi_template.svg"
    target: Path = CURRENT_DIR / "_static" / "pypi.svg"
    with open(str(template), encoding="utf8") as f:
        svg: str = string.Template(f.read()).substitute(version=version)
    with open(str(target), "w", encoding="utf8") as f:
        f.write(svg)


def replace_pr_numbers_with_links(content: str) -> str:
    """Replaces all PR numbers with the corresponding GitHub link."""

    base_url = "https://github.com/psf/black/pull/"
    pr_num_regex = re.compile(r"\(#(\d+)\)")

    def num_to_link(match: re.Match[str]) -> str:
        number = match.group(1)
        url = f"{base_url}{number}"
        return f"([#{number}]({url}))"

    return pr_num_regex.sub(num_to_link, content)


def handle_include_read(
    app: Sphinx,
    relative_path: Path,
    parent_docname: str,
    content: list[str],
) -> None:
    """Handler for the include-read sphinx event."""
    if parent_docname == "change_log":
        content[0] = replace_pr_numbers_with_links(content[0])


def setup(app: Sphinx) -> None:
    """Sets up a minimal sphinx extension."""
    app.connect("include-read", handle_include_read)


# Necessary so Click doesn't hit an encode error when called by
# sphinxcontrib-programoutput on Windows.
os.putenv("pythonioencoding", "utf-8")

# -- Project information -----------------------------------------------------

project = "Black"
copyright = "2018-Present, Łukasz Langa and contributors to Black"
author = "Łukasz Langa and contributors to Black"

# Autopopulate version
# The version, including alpha/beta/rc tags, but not commit hash and datestamps
release = version("black").split("+")[0]
# The short X.Y version.
version = release
for sp in "abcfr":
    version = version.split(sp)[0]

make_pypi_svg(release)


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "4.4"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinxcontrib.programoutput",
    "sphinx_copybutton",
]

# If you need extensions of a certain version or higher, list them here.
needs_extensions = {"myst_parser": "0.13.7"}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# We need headers to be linkable to so ask MyST-Parser to autogenerate anchor IDs for
# headers up to and including level 3.
myst_heading_anchors = 3

# Prettier support formatting some MyST syntax but not all, so let's disable the
# unsupported yet still enabled by default ones.
myst_disable_syntax = [
    "colon_fence",
    "myst_block_break",
    "myst_line_comment",
    "math_block",
]

# Optional MyST Syntaxes
myst_enable_extensions = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_logo = "_static/logo2-readme.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "blackdoc"


# -- Options for LaTeX output ------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [(
    master_doc,
    "black.tex",
    "Documentation for Black",
    "Łukasz Langa and contributors to Black",
    "manual",
)]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "black", "Documentation for Black", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [(
    master_doc,
    "Black",
    "Documentation for Black",
    author,
    "Black",
    "The uncompromising Python code formatter",
    "Miscellaneous",
)]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]


# -- Extension configuration -------------------------------------------------

autodoc_member_order = "bysource"

#  -- sphinx-copybutton configuration ----------------------------------------
copybutton_prompt_text = (
    r">>> |\.\.\. |> |\$ |\# | In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
)
copybutton_prompt_is_regexp = True
copybutton_remove_prompts = True

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"<name>": ("https://docs.python.org/3/", None)}
