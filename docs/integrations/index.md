# Integrations

```{toctree}
---
hidden:
---

editors
github_actions
source_version_control
```

_Black_ can be integrated into many environments, providing a better and smoother
experience. Documentation for integrating _Black_ with a tool can be found for the
following areas:

- {doc}`Editor / IDE <./editors>`
- {doc}`GitHub Actions <./github_actions>`
- {doc}`Source version control <./source_version_control>`

Editors and tools not listed will require external contributions.

Patches welcome! ✨ 🍰 ✨

## Formatting doctests and docstrings

While _Black_ itself does not format code within docstrings or doctests, there are
third-party tools that can apply Black formatting to these areas:

### blacken-docs

[blacken-docs](https://github.com/adamchainz/blacken-docs) formats code blocks in
documentation files (`.rst`, `.md`, `.tex`) and in docstrings. It supports:

- Python code blocks in Markdown and reStructuredText
- Doctests in Markdown/reStructuredText blocks within docstrings

Installation:

```sh
pip install blacken-docs
```

Usage:

```sh
blacken-docs README.md docs/*.rst
```

**Note**: blacken-docs requires doctests to be within Markdown or reStructuredText code
blocks (e.g., ` ```pycon ` or `.. code-block:: pycon`). It does not support plain
doctests directly in docstrings outside of these blocks.

### blackdoc

[blackdoc](https://github.com/keewis/blackdoc) formats doctests in Python files,
including plain doctests in docstrings. It supports:

- Plain doctests in docstrings (no Markdown/reStructuredText blocks required)
- Doctests in documentation files

Installation:

```sh
pip install blackdoc
```

Usage:

```sh
blackdoc my_module.py
```

**Note**: blackdoc is not actively maintained, so it may not receive updates for newer
Black features or Python syntax.

### Choosing a tool

- If your doctests are in **documentation files** (`.md`, `.rst`), use **blacken-docs**
- If your doctests are in **docstrings with Markdown/reStructuredText blocks**, use
  **blacken-docs**
- If your doctests are **plain doctests in docstrings** (without special formatting),
  use **blackdoc**

Be aware that these tools may not format code identically in all cases. If you need both
tools, test carefully to ensure they produce compatible results.

Any tool can pipe code through _Black_ using its stdio mode (just
[use `-` as the file name](https://www.tldp.org/LDP/abs/html/special-chars.html#DASHREF2)).
The formatted code will be returned on stdout (unless `--check` was passed). _Black_
will still emit messages on stderr but that shouldn't affect your use case.

This can be used for example with PyCharm's or IntelliJ's
[File Watchers](https://www.jetbrains.com/help/pycharm/file-watchers.html).
