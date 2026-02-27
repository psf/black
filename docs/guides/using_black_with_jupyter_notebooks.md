# Using _Black_ with Jupyter Notebooks

_Black_ has built-in support for formatting Jupyter Notebooks (`.ipynb` files). This
guide covers installation, usage, configuration, and common questions.

## Installation

To format Jupyter Notebooks, install _Black_ with the `jupyter` extra:

```sh
pip install "black[jupyter]"
```

This installs the additional `tokenize-rt` dependency needed for notebook support.

```{note}
Without the `jupyter` extra, _Black_ will not be able to format `.ipynb` files.
```

## Basic usage

Once installed, you can format notebooks the same way you format Python files:

```sh
black notebook.ipynb
```

You can also format entire directories containing a mix of `.py` and `.ipynb` files:

```sh
black .
```

_Black_ will automatically detect Jupyter Notebooks by their `.ipynb` extension and
format them accordingly.

### Formatting via standard input

If you're piping notebook content on standard input, use the `--ipynb` flag to tell
_Black_ to treat the input as a Jupyter Notebook:

```sh
cat notebook.ipynb | black --ipynb -
```

## How it works

_Black_ formats the Python code cells in your notebook while preserving:

- Markdown cells
- Cell outputs
- Cell metadata
- Notebook metadata

Only the source code within Python code cells is reformatted.

## Cell magics

_Black_ understands IPython magics, but is conservative about which cells it will
format. By default, _Black_ recognizes standard IPython magics.

### Custom python cell magics

If you use custom cell magics that contain Python code, you can tell _Black_ about them
using the `--python-cell-magics` flag:

```sh
black --python-cell-magics writefile notebook.ipynb
```

This also works in `pyproject.toml`:

```toml
[tool.black]
python-cell-magics = ["writefile", "my_custom_magic"]
```

## Cells that _Black_ will skip

_Black_ is cautious about formatting notebook cells. The following cells will **not** be
formatted:

- **Automagics** — e.g. `pip install black` (without the `%` prefix)
- **Non-Python cell magics** — e.g. `%%writefile` (unless added via
  `--python-cell-magics`)
- **Multiline magics** — e.g.:

  ```python
  %timeit f(1, \
          2, \
          3)
  ```

- **IPython internal calls** — code that `IPython`'s `TransformerManager` would
  transform, e.g.:

  ```python
  get_ipython().system('ls')
  ```

- **Invalid syntax** — as it cannot be safely distinguished from automagics without a
  running IPython kernel.

If you notice a cell is not being formatted, it is likely because it contains one of the
above constructs.

## Editor integration

Many editors and IDEs support running _Black_ on Jupyter Notebooks:

- **VS Code**: The Python extension supports formatting notebooks with _Black_. Set
  `"notebook.formatOnSave.enabled": true` and configure _Black_ as your formatter.
- **JupyterLab**: You can use
  [jupyterlab-code-formatter](https://github.com/ryantam626/jupyterlab-code-formatter)
  to run _Black_ from within JupyterLab.

## Pre-commit hook

If you use [pre-commit](https://pre-commit.com/), _Black_ will format notebooks
automatically. Make sure to include `jupyter` in the `additional_dependencies`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 25.1.0
    hooks:
      - id: black-jupyter
```

The `black-jupyter` hook ID is specifically designed for formatting both Python files
and Jupyter Notebooks.

```{note}
If you only use the `black` hook ID (without `-jupyter`), notebooks will **not** be
formatted.
```
