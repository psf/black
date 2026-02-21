# Formatting Jupyter Notebooks

_Black_ has native support for formatting Jupyter Notebooks. This page covers everything
you need to know about using _Black_ with notebooks.

## Installation

To format Jupyter Notebooks, you need to install _Black_ with the `jupyter` extra:

```sh
pip install "black[jupyter]"
```

If you use pipx:

```sh
pipx install black[jupyter]
```

This installs the additional dependencies required to parse and format `.ipynb` files.

## Basic Usage

Format a single notebook:

```sh
black my_notebook.ipynb
```

Format all notebooks in a directory:

```sh
black notebooks/
```

Check if notebooks would be reformatted without making changes:

```sh
black --check my_notebook.ipynb
```

See the diff of what would change:

```sh
black --diff my_notebook.ipynb
```

## How It Works

_Black_ formats the code cells in your Jupyter Notebook while preserving:

- Markdown cells (unchanged)
- Cell outputs
- Cell metadata
- Notebook metadata

Only Python code cells are formatted according to _Black_'s style.

## Cells That Won't Be Formatted

_Black_ is conservative about which cells it formats to avoid breaking notebook
functionality. The following cells are **skipped**:

### IPython Automagics

Cells containing automagics (commands that aren't valid Python):

```python
# This cell won't be formatted
%pip install black
%load_ext autoreload
```

### Non-Python Cell Magics

Cells with cell magics that contain non-Python code:

```python
# This cell won't be formatted
%%writefile script.py
print("hello")
```

You can tell _Black_ that certain cell magics actually contain Python code using the
`--python-cell-magics` option:

```sh
black --python-cell-magics writefile,timeit my_notebook.ipynb
```

### Multiline Magics

Cells with multiline magics:

```python
# This cell won't be formatted
%matplotlib \
    inline
```

### IPython Transformer Syntax

Code that IPython's `TransformerManager` would transform:

```python
# This cell won't be formatted
get_ipython().run_line_magic('pip', 'install black')
```

### Invalid Syntax

Cells with invalid Python syntax that can't be safely distinguished from automagics
(without a running IPython kernel).

## Configuration

All standard _Black_ configuration options work with Jupyter Notebooks. Configure via
`pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py311']
```

### Jupyter-Specific Options

**`--python-cell-magics`**: Specify cell magics that should be treated as Python code:

```sh
black --python-cell-magics writefile,timeit notebook.ipynb
```

In `pyproject.toml`:

```toml
[tool.black]
python-cell-magics = ["writefile", "timeit"]
```

**`--skip-magic-trailing-comma`**: Skip adding trailing commas to cell magics:

```sh
black --skip-magic-trailing-comma notebook.ipynb
```

## Pre-commit Integration

To automatically format notebooks with [pre-commit](https://pre-commit.com/), use the
`black-jupyter` hook instead of the regular `black` hook:

```yaml
repos:
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 26.1.0
    hooks:
      - id: black-jupyter
        language_version: python3.11
```

See [Version control integration](../integrations/source_version_control.md) for more
details on using _Black_ with pre-commit.

## Troubleshooting

### Why isn't my cell being formatted?

Most likely because it contains one of the
[unsupported patterns](#cells-that-wont-be-formatted) listed above. _Black_ is
intentionally conservative to avoid breaking notebook functionality.

To see what _Black_ would do, run with `--diff`:

```sh
black --diff my_notebook.ipynb
```
