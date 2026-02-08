# Jupyter Notebooks

Black supports formatting Jupyter Notebooks natively. This page provides comprehensive information on how to install, configure, and use Black with Jupyter Notebooks.

## Installation

To format Jupyter Notebooks with Black, you need to install Black with the `jupyter` extra:

```sh
pip install "black[jupyter]"
```

If you use pipx:

```sh
pipx install black --preinstall jupyter
```

The Jupyter extra installs the necessary dependencies for Black to read and format Jupyter Notebook files (`.ipynb`).

## Basic Usage

Black can format Jupyter Notebooks just like regular Python files:

```sh
black notebook.ipynb
```

You can also format entire directories containing notebooks:

```sh
black notebooks/
```

Black will automatically detect `.ipynb` files and format them appropriately.

## Command Line Options

### `--ipynb`

Format all input files like Jupyter Notebooks regardless of file extension. This is useful when piping source on standard input.

```sh
cat notebook.txt | black --ipynb -
```

### `--python-cell-magics`

When processing Jupyter Notebooks, add the given magic to the list of known python-magics. This is useful for formatting cells with custom python magics.

```sh
black --python-cell-magics writefile notebook.ipynb
```

You can specify multiple custom magics:

```sh
black --python-cell-magics writefile --python-cell-magics save notebook.ipynb
```

## Configuration

You can configure Jupyter-specific options in your `pyproject.toml`:

```toml
[tool.black]
# Add custom Python cell magics
python-cell-magics = ["writefile", "save"]
```

All other Black configuration options (line length, target version, etc.) apply to notebooks as well:

```toml
[tool.black]
line-length = 100
target-version = ["py311", "py312"]
python-cell-magics = ["writefile"]
```

## What Gets Formatted

Black formats code cells in Jupyter Notebooks. However, Black is intentionally conservative about what it formats to avoid breaking notebook functionality.

### Cells That Are Formatted

- Standard Python code cells
- Cells with known Python cell magics (specified via `--python-cell-magics`)

### Cells That Are Not Formatted

Black will skip cells containing any of the following:

- **Automagics**: Commands like `pip install black`, `ls`, `cd`, etc.
- **Non-Python cell magics**: Magic commands like `%%writefile`, `%%bash`, `%%html`, etc. You can add these to the list of Python cell magics with `--python-cell-magics` if they contain Python code.
- **Multiline magics**: Magic commands that span multiple lines with line continuations:

  ```python
  %timeit f(1, \
          2, \
          3)
  ```

- **IPython system calls**: Code that IPython's TransformerManager would transform:

  ```python
  get_ipython().system('ls')
  ```

- **Invalid syntax**: Code with syntax errors, as it can't be safely distinguished from automagics without a running IPython kernel.

## Integration with Pre-commit

You can use Black with Jupyter Notebooks in your pre-commit configuration:

```yaml
repos:
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.12.0
    hooks:
      - id: black
        types_or: [python, pyi, jupyter]
      - id: black-jupyter
        # Deprecated: use the main black hook with `types_or` instead
```

The `black` hook with `types_or: [python, pyi, jupyter]` will format both Python files and Jupyter Notebooks.

## Integration with Editors

Many editor integrations for Black support Jupyter Notebooks. Check the [Editor Integration documentation](../integrations/editors.md) for specific instructions for your editor.

### Jupyter Notebook Interface

Black does not have a built-in extension for the Jupyter Notebook interface. However, you can:

1. Format notebooks from the command line before committing
2. Use Jupyter Lab extensions like `jupyterlab-code-formatter` which supports Black
3. Run Black through pre-commit hooks

### VS Code

The Python extension for VS Code supports formatting Jupyter Notebooks with Black. Make sure you have:

1. Installed Black with the `jupyter` extra
2. Set Black as your Python formatter in VS Code settings
3. The extension will automatically detect and format notebook cells

## Troubleshooting

### Why is my cell not formatted?

If a cell isn't being formatted, it likely contains one of the patterns Black skips (see "Cells That Are Not Formatted" above). You can:

- Check if the cell contains automagics or cell magics
- If it contains a custom Python cell magic, add it with `--python-cell-magics`
- Verify the cell doesn't have syntax errors

### Formatting differences

Note that Black may format notebook code differently than it would format the same code in a `.py` file due to the presence of IPython-specific syntax. This is intentional to maintain compatibility with the Jupyter environment.

## Examples

Format a single notebook:

```sh
black my_analysis.ipynb
```

Format all notebooks in a directory:

```sh
black notebooks/
```

Format with custom cell magics:

```sh
black --python-cell-magics writefile --python-cell-magics capture analysis.ipynb
```

Check if notebooks need formatting (useful in CI):

```sh
black --check notebooks/
```

Show diff of changes without modifying files:

```sh
black --diff notebooks/
```
