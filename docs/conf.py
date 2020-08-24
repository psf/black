# -*- coding: utf-8 -*-
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
from pathlib import Path
import re
import string
from typing import Callable, Dict, List, Optional, Pattern, Tuple, Set
from dataclasses import dataclass
import logging

from pkg_resources import get_distribution

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

LOG = logging.getLogger(__name__)

CURRENT_DIR = Path(__file__).parent
README = CURRENT_DIR / ".." / "README.md"
REFERENCE_DIR = CURRENT_DIR / "reference"
STATIC_DIR = CURRENT_DIR / "_static"


@dataclass
class SrcRange:
    """Tracks which part of a file to get a section's content.

    Data:
        start_line: The line where the section starts (i.e. its sub-header) (inclusive).
        end_line: The line where the section ends (usually next sub-header) (exclusive).
    """

    start_line: int
    end_line: int


@dataclass
class DocSection:
    """Tracks information about a section of documentation.

    Data:
        name: The section's name. This will used to detect duplicate sections.
        src: The filepath to get its contents.
        processors: The processors to run before writing the section to CURRENT_DIR.
        out_filename: The filename to use when writing the section to CURRENT_DIR.
        src_range: The line range of SRC to gets its contents.
    """

    name: str
    src: Path
    src_range: SrcRange = SrcRange(0, 1_000_000)
    out_filename: str = ""
    processors: Tuple[Callable, ...] = ()

    def get_out_filename(self) -> str:
        if not self.out_filename:
            return self.name + ".md"
        else:
            return self.out_filename


def make_pypi_svg(version: str) -> None:
    template: Path = CURRENT_DIR / "_static" / "pypi_template.svg"
    target: Path = CURRENT_DIR / "_static" / "pypi.svg"
    with open(str(template), "r", encoding="utf8") as f:
        svg: str = string.Template(f.read()).substitute(version=version)
    with open(str(target), "w", encoding="utf8") as f:
        f.write(svg)


def make_filename(line: str) -> str:
    non_letters: Pattern = re.compile(r"[^a-z]+")
    filename: str = line[3:].rstrip().lower()
    filename = non_letters.sub("_", filename)
    if filename.startswith("_"):
        filename = filename[1:]
    if filename.endswith("_"):
        filename = filename[:-1]
    return filename + ".md"


def get_contents(section: DocSection) -> str:
    """Gets the contents for the DocSection."""
    contents: List[str] = []
    src: Path = section.src
    start_line: int = section.src_range.start_line
    end_line: int = section.src_range.end_line
    with open(src, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if lineno >= start_line and lineno < end_line:
                contents.append(line)
    result = "".join(contents)
    # Let's make Prettier happy with the amount of trailing newlines in the sections.
    if result.endswith("\n\n"):
        result = result[:-1]
    if not result.endswith("\n"):
        result = result + "\n"
    return result


def get_sections_from_readme() -> List[DocSection]:
    """Gets the sections from README so they can be processed by process_sections.

    It opens README and goes down line by line looking for sub-header lines which
    denotes a section. Once it finds a sub-header line, it will create a DocSection
    object with all of the information currently available. Then on every line, it will
    track the ending line index of the section. And it repeats this for every sub-header
    line it finds.
    """
    sections: List[DocSection] = []
    section: Optional[DocSection] = None
    with open(README, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if line.startswith("## "):
                filename = make_filename(line)
                section_name = filename[:-3]
                section = DocSection(
                    name=str(section_name),
                    src=README,
                    src_range=SrcRange(lineno, lineno),
                    out_filename=filename,
                    processors=(fix_headers,),
                )
                sections.append(section)
            if section is not None:
                section.src_range.end_line += 1
    return sections


def fix_headers(contents: str) -> str:
    """Fixes the headers of sections copied from README.

    Removes one octothorpe (#) from all headers since the contents are no longer nested
    in a root document (i.e. the README).
    """
    lines: List[str] = contents.splitlines()
    fixed_contents: List[str] = []
    for line in lines:
        if line.startswith("##"):
            line = line[1:]
        fixed_contents.append(line + "\n")  # splitlines strips the leading newlines
    return "".join(fixed_contents)


def process_sections(
    custom_sections: List[DocSection], readme_sections: List[DocSection]
) -> None:
    """Reads, processes, and writes sections to CURRENT_DIR.

    For each section, the contents will be fetched, processed by processors
    required by the section, and written to CURRENT_DIR. If it encounters duplicate
    sections (i.e. shares the same name attribute), it will skip processing the
    duplicates.

    It processes custom sections before the README generated sections so sections in the
    README can be overwritten with custom options.
    """
    processed_sections: Dict[str, DocSection] = {}
    modified_files: Set[Path] = set()
    sections: List[DocSection] = custom_sections
    sections.extend(readme_sections)
    for section in sections:
        if section.name in processed_sections:
            LOG.warning(
                f"Skipping '{section.name}' from '{section.src}' as it is a duplicate"
                f" of a custom section from '{processed_sections[section.name].src}'"
            )
            continue

        LOG.info(f"Processing '{section.name}' from '{section.src}'")
        target_path: Path = CURRENT_DIR / section.get_out_filename()
        if target_path in modified_files:
            LOG.warning(
                f"{target_path} has been already written to, its contents will be"
                " OVERWRITTEN and notices will be duplicated"
            )
        contents: str = get_contents(section)

        # processors goes here
        if fix_headers in section.processors:
            contents = fix_headers(contents)

        with open(target_path, "w", encoding="utf-8") as f:
            if section.src.suffix == ".md" and section.src != target_path:
                rel = section.src.resolve().relative_to(CURRENT_DIR.parent)
                f.write(f'[//]: # "NOTE: THIS FILE WAS AUTOGENERATED FROM {rel}"\n\n')
            f.write(contents)
        processed_sections[section.name] = section
        modified_files.add(target_path)


# -- Project information -----------------------------------------------------

project = "Black"
copyright = "2020, Łukasz Langa and contributors to Black"
author = "Łukasz Langa and contributors to Black"

# Autopopulate version
# The version, including alpha/beta/rc tags, but not commit hash and datestamps
release = get_distribution("black").version.split("+")[0]
# The short X.Y version.
version = release
for sp in "abcfr":
    version = version.split(sp)[0]

custom_sections = [
    DocSection("the_black_code_style", CURRENT_DIR / "the_black_code_style.md"),
    DocSection("editor_integration", CURRENT_DIR / "editor_integration.md"),
    DocSection("blackd", CURRENT_DIR / "blackd.md"),
    DocSection("black_primer", CURRENT_DIR / "black_primer.md"),
    DocSection("contributing_to_black", CURRENT_DIR / ".." / "CONTRIBUTING.md"),
    DocSection("change_log", CURRENT_DIR / ".." / "CHANGES.md"),
]

# Sphinx complains when there is a source file that isn't referenced in any of the docs.
# Since some sections autogenerated from the README are unused warnings will appear.
#
# Sections must be listed to what their name is when passed through make_filename().
blocklisted_sections_from_readme = {
    "license",
    "pragmatism",
    "testimonials",
    "used_by",
}

make_pypi_svg(release)
readme_sections = get_sections_from_readme()
readme_sections = [
    x for x in readme_sections if x.name not in blocklisted_sections_from_readme
]

process_sections(custom_sections, readme_sections)


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "3.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "recommonmark",
]

# If you need extensions of a certain version or higher, list them here.
needs_extensions = {"recommonmark": "0.5"}

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
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "sourcelink.html",
        "searchbox.html",
    ]
}

html_theme_options = {
    "show_related": False,
    "description": "“Any color you like.”",
    "github_button": True,
    "github_user": "psf",
    "github_repo": "black",
    "github_type": "star",
    "show_powered_by": True,
    "fixed_sidebar": True,
    "logo": "logo2.png",
    "travis_button": True,
}


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

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "black.tex",
        "Documentation for Black",
        "Łukasz Langa and contributors to Black",
        "manual",
    )
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "black", "Documentation for Black", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "Black",
        "Documentation for Black",
        author,
        "Black",
        "The uncompromising Python code formatter",
        "Miscellaneous",
    )
]


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

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"https://docs.python.org/3/": None}
