# Cercis

[![](https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Red_bud_2009.jpg/320px-Red_bud_2009.jpg)](https://en.wikipedia.org/wiki/Cercis)

_**Cercis**_ /ˈsɜːrsɪs/ is a Python code formatter that is more configurable than
[Black](https://github.com/psf/black) (a popular Python code formatter).

[_Cercis_](https://en.wikipedia.org/wiki/Cercis) is also a name of a deciduous tree that
boasts vibrant pink to purple-hued flowers, which bloom in early spring.

This code repository is forked from and directly inspired by
[Black](https://github.com/psf/black). The original license of Black is included in this
repository (see [LICENSE_ORIGINAL](./LICENSE_ORIGINAL)).

## 1. Motivations

While we like the idea of auto-formatting and making code readable, we take issue with
some style choices and the lack of configurability of the Black formatter. We
acknowledge that people have different style preferences, and we believe this is totally
OK.

Therefore, _Cercis_ aims at providing some configurability beyond Black's limited
offering.

## 2. Installation and usage

### 2.1. Installation

_Cercis_ can be installed by running `pip install cercis`. It requires Python 3.7+ to
run. If you want to format Jupyter Notebooks, install with
`pip install "cercis[jupyter]"`.

### 2.2. Usage

#### 2.2.1. Command line usage

To get started right away with sensible defaults:

```sh
cercis {source_file_or_directory}
```

You can run _Cercis_ as a package if running it as a script doesn't work:

```sh
python -m cercis {source_file_or_directory}
```

The commands above reformat entire file(s) in place.

#### 2.2.2. As pre-commit hook

To format Python files (.py), put the following into your `.pre-commit-config.yaml`
file. Remember to replace `<VERSION>` with your version of this tool (such as `v0.1.0`):

```yaml
- repo: https://github.com/jsh9/cercis
  rev: <VERSION>
  hooks:
    - id: cercis
```

To format Jupyter notebooks (.ipynb), put the following into your
`.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/jsh9/cercis
  rev: <VERSION>
  hooks:
    - id: cercis-jupyter
```

See [pre-commit](https://github.com/pre-commit/pre-commit) for more instructions.

## 3. The code style

The code style in _Cercis_ is largely consistent with the
[style of of _Black_](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html).

The differences are summarized below:

### 3.1. Extra indentation of at function definition

For this example input:

```python
def very_important_function(template: str, *variables, file: os.PathLike, engine: str, header: bool = True, debug: bool = False):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, 'w') as f:
        ...
```

_Black_ formats it as this:

```python
def very_important_function(
    template: str,
    *variables,
    file: os.PathLike,
    engine: str,
    header: bool = True,
    debug: bool = False,
):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, "w") as f:
        ...
```

while _Cercis_ formats it as:

```python
def very_important_function(
        template: str,
        *variables,
        file: os.PathLike,
        engine: str,
        header: bool = True,
        debug: bool = False,
):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, "w") as f:
        ...
```

We choose to indent an extra 4 spaces because it adds a clear visual separation between
the function name and the argument list. Not adding extra indentation is also called out
as wrong in the the official
[PEP8 style guide](https://peps.python.org/pep-0008/#indentation).

## 4. Configuration

_Cercis_ is able to read project-specific default values for its command line options
from a `pyproject.toml` file. This is especially useful for specifying custom
`--include` and `--exclude`/`--force-exclude`/`--extend-exclude` patterns for your
project.
