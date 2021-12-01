# Frequently Asked Questions

The most common questions and issues users face are aggregated to this FAQ.

```{contents}
:local:
:backlinks: none
```

## Does Black have an API?

Not yet. _Black_ is fundamentally a command line tool. Many
[integrations](integrations/index.rst) are provided, but a Python interface is not one
of them. A simple API is being [planned](https://github.com/psf/black/issues/779)
though.

## Is Black safe to use?

Yes, for the most part. _Black_ is strictly about formatting, nothing else. But because
_Black_ is still in [beta](index.rst), some edges are still a bit rough. To combat
issues, the equivalence of code after formatting is
[checked](the_black_code_style/current_style.md#ast-before-and-after-formatting) with
limited special cases where the code is allowed to differ. If issues are found, an error
is raised and the file is left untouched. Magical comments that influence linters and
other tools, such as `# noqa`, may be moved by _Black_. See below for more details.

## How stable is Black's style?

Quite stable. _Black_ aims to enforce one style and one style only, with some room for
pragmatism. However, _Black_ is still in beta so style changes are both planned and
still proposed on the issue tracker. See
[The Black Code Style](the_black_code_style/index.rst) for more details.

Starting in 2022, the formatting output will be stable for the releases made in the same
year (other than unintentional bugs). It is possible to opt-in to the latest formatting
styles, using the `--future` flag.

## Why is my file not formatted?

Most likely because it is ignored in `.gitignore` or excluded with configuration. See
[file collection and discovery](usage_and_configuration/file_collection_and_discovery.md)
for details.

## Why is my Jupyter Notebook cell not formatted?

_Black_ is timid about formatting Jupyter Notebooks. Cells containing any of the
following will not be formatted:

- automagics (e.g. `pip install black`)
- non-Python cell magics (e.g. `%%writeline`)
- multiline magics, e.g.:

  ```python
  %timeit f(1, \
          2, \
          3)
  ```

- code which `IPython`'s `TransformerManager` would transform magics into, e.g.:

  ```python
  get_ipython().system('ls')
  ```

- invalid syntax, as it can't be safely distinguished from automagics in the absence of
  a running `IPython` kernel.

## Why are Flake8's E203 and W503 violated?

Because they go against PEP 8. E203 falsely triggers on list
[slices](the_black_code_style/current_style.md#slices), and adhering to W503 hinders
readability because operators are misaligned. Disable W503 and enable the
disabled-by-default counterpart W504. E203 should be disabled while changes are still
[discussed](https://github.com/PyCQA/pycodestyle/issues/373).

## Does Black support Python 2?

```{warning}
Python 2 support has been deprecated since 21.10b0.

This support will be dropped in the first stable release, expected for January 2022.
See [The Black Code Style](the_black_code_style/index.rst) for details.
```

For formatting, yes! [Install](getting_started.md#installation) with the `python2` extra
to format Python 2 files too! In terms of running _Black_ though, Python 3.6 or newer is
required.

## Why does my linter or typechecker complain after I format my code?

Some linters and other tools use magical comments (e.g., `# noqa`, `# type: ignore`) to
influence their behavior. While Black does its best to recognize such comments and leave
them in the right place, this detection is not and cannot be perfect. Therefore, you'll
sometimes have to manually move these comments to the right place after you format your
codebase with _Black_.

## Can I run Black with PyPy?

Yes, there is support for PyPy 3.7 and higher. You cannot format Python 2 files under
PyPy, because PyPy's inbuilt ast module does not support this.

## Why does Black not detect syntax errors in my code?

_Black_ is an autoformatter, not a Python linter or interpreter. Detecting all syntax
errors is not a goal. It can format all code accepted by CPython (if you find an example
where that doesn't hold, please report a bug!), but it may also format some code that
CPython doesn't accept.
