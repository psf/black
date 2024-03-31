# Using _Black_ with other tools

## Black compatible configurations

All of Black's changes are harmless (or at least, they should be), but a few do conflict
against other tools. It is not uncommon to be using other tools alongside _Black_ like
linters and type checkers. Some of them need a bit of tweaking to resolve the conflicts.
Listed below are _Black_ compatible configurations in various formats for the common
tools out there.

**Please note** that _Black_ only supports the TOML file format for its configuration
(e.g. `pyproject.toml`). The provided examples are to only configure their corresponding
tools, using **their** supported file formats.

Compatible configuration files can be
[found here](https://github.com/psf/black/blob/main/docs/compatible_configs/).

### isort

[isort](https://pypi.org/p/isort/) helps to sort and format imports in your Python code.
_Black_ also formats imports, but in a different way from isort's defaults which leads
to conflicting changes.

#### Profile

Since version 5.0.0, isort supports
[profiles](https://pycqa.github.io/isort/docs/configuration/profiles.html) to allow easy
interoperability with common code styles. You can set the black profile in any of the
[config files](https://pycqa.github.io/isort/docs/configuration/config_files.html)
supported by isort. Below, an example for `pyproject.toml`:

```toml
[tool.isort]
profile = "black"
```

#### Custom Configuration

If you're using an isort version that is older than 5.0.0 or you have some custom
configuration for _Black_, you can tweak your isort configuration to make it compatible
with _Black_. Below, an example for `.isort.cfg`:

```
multi_line_output = 3
include_trailing_comma = True
force_grid_wrap = 0
use_parentheses = True
ensure_newline_before_comments = True
line_length = 88
```

#### Why those options above?

_Black_ wraps imports that surpass `line-length` by moving identifiers onto separate
lines and by adding a trailing comma after each. A more detailed explanation of this
behaviour can be
[found here](../the_black_code_style/current_style.md#how-black-wraps-lines).

isort's default mode of wrapping imports that extend past the `line_length` limit is
"Grid".

```py3
from third_party import (lib1, lib2, lib3,
                         lib4, lib5, ...)
```

This style is incompatible with _Black_, but isort can be configured to use a different
wrapping mode called "Vertical Hanging Indent" which looks like this:

```py3
from third_party import (
    lib1,
    lib2,
    lib3,
    lib4,
)
```

This style is _Black_ compatible and can be achieved by `multi-line-output = 3`. Also,
as mentioned above, when wrapping long imports _Black_ puts a trailing comma and uses
parentheses. isort should follow the same behaviour and passing the options
`include_trailing_comma = True` and `use_parentheses = True` configures that.

The option `force_grid_wrap = 0` is just to tell isort to only wrap imports that surpass
the `line_length` limit.

Finally, isort should be told to wrap imports when they surpass _Black_'s default limit
of 88 characters via `line_length = 88` as well as
`ensure_newline_before_comments = True` to ensure spacing import sections with comments
works the same as with _Black_.

**Please note** `ensure_newline_before_comments = True` only works since isort >= 5 but
does not break older versions so you can keep it if you are running previous versions.

#### Formats

<details>
<summary>.isort.cfg</summary>

```ini
[settings]
profile = black
```

</details>

<details>
<summary>setup.cfg</summary>

```ini
[isort]
profile = black
```

</details>

<details>
<summary>pyproject.toml</summary>

```toml
[tool.isort]
profile = 'black'
```

</details>

<details>
<summary>.editorconfig</summary>

```ini
[*.py]
profile = black
```

</details>

### pycodestyle

[pycodestyle](https://pycodestyle.pycqa.org/) is a code linter. It warns you of syntax
errors, possible bugs, stylistic errors, etc. For the most part, pycodestyle follows
[PEP 8](https://www.python.org/dev/peps/pep-0008/) when warning about stylistic errors.
There are a few deviations that cause incompatibilities with _Black_.

#### Configuration

```
max-line-length = 88
ignore = E203,E701
```

(labels/why-pycodestyle-warnings)=

#### Why those options above?

##### `max-line-length`

As with isort, pycodestyle should be configured to allow lines up to the length limit of
`88`, _Black_'s default.

##### `E203`

In some cases, as determined by PEP 8, _Black_ will enforce an equal amount of
whitespace around slice operators. Due to this, pycodestyle will raise
`E203 whitespace before ':'` warnings. Since this warning is not PEP 8 compliant, it
should be disabled.

##### `E701` / `E704`

_Black_ will collapse implementations of classes and functions consisting solely of `..`
to a single line. This matches how such examples are formatted in PEP 8. It remains true
that in all other cases Black will prevent multiple statements on the same line, in
accordance with PEP 8 generally discouraging this.

However, `pycodestyle` does not mirror this logic and may raise
`E701 multiple statements on one line (colon)` in this situation. Its
disabled-by-default `E704 multiple statements on one line (def)` rule may also raise
warnings and should not be enabled.

##### `W503`

When breaking a line, _Black_ will break it before a binary operator. This is compliant
with PEP 8 as of
[April 2016](https://github.com/python/peps/commit/c59c4376ad233a62ca4b3a6060c81368bd21e85b#diff-64ec08cc46db7540f18f2af46037f599).
There's a disabled-by-default warning in Flake8 which goes against this PEP 8
recommendation called `W503 line break before binary operator`. It should not be enabled
in your configuration. You can use its counterpart
`W504 line break after binary operator` instead.

#### Formats

<details>
<summary>setup.cfg, .pycodestyle, tox.ini</summary>

```ini
[pycodestyle]
max-line-length = 88
ignore = E203,E701
```

</details>

### Flake8

[Flake8](https://pypi.org/p/flake8/) is a wrapper around multiple linters, including
pycodestyle. As such, it has many of the same issues.

#### Bugbear

It's recommended to use [the Bugbear plugin](https://github.com/PyCQA/flake8-bugbear)
and enable
[its B950 check](https://github.com/PyCQA/flake8-bugbear#opinionated-warnings#:~:text=you%20expect%20it.-,B950,-%3A%20Line%20too%20long)
instead of using Flake8's E501, because it aligns with
[Black's 10% rule](labels/line-length).

Install Bugbear and use the following config:

```
[flake8]
max-line-length = 80
extend-select = B950
extend-ignore = E203,E501,E701
```

#### Minimal Configuration

In cases where you can't or don't want to install Bugbear, you can use this minimally
compatible config:

```
[flake8]
max-line-length = 88
extend-ignore = E203,E701
```

#### Why those options above?

See [the pycodestyle section](labels/why-pycodestyle-warnings) above.

#### Formats

<details>
<summary>.flake8, setup.cfg, tox.ini</summary>

```ini
[flake8]
max-line-length = 88
extend-ignore = E203,E701
```

</details>

### Pylint

[Pylint](https://pypi.org/p/pylint/) is also a code linter like Flake8. It has many of
the same checks as Flake8 and more. It particularly has more formatting checks regarding
style conventions like variable naming.

#### Configuration

```
max-line-length = 88
```

#### Why those options above?

Pylint should be configured to only complain about lines that surpass `88` characters
via `max-line-length = 88`.

If using `pylint<2.6.0`, also disable `C0326` and `C0330` as these are incompatible with
_Black_ formatting and have since been removed.

#### Formats

<details>
<summary>pylintrc</summary>

```ini
[format]
max-line-length = 88
```

</details>

<details>
<summary>setup.cfg</summary>

```cfg
[pylint]
max-line-length = 88
```

</details>

<details>
<summary>pyproject.toml</summary>

```toml
[tool.pylint.format]
max-line-length = "88"
```

</details>
