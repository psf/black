<h2 align="center">The Compromising Code Formatter</h2>

<p align="center">
<a href="https://github.com/psf/prism/actions"><img alt="Actions Status" src="https://github.com/psf/prism/workflows/Test/badge.svg"></a>
<a href="https://prism.readthedocs.io/en/stable/?badge=stable"><img alt="Documentation Status" src="https://readthedocs.org/projects/prism/badge/?version=stable"></a>
<a href="https://coveralls.io/github/psf/prism?branch=main"><img alt="Coverage Status" src="https://coveralls.io/repos/github/psf/prism/badge.svg?branch=main"></a>
<a href="https://github.com/psf/prism/blob/main/LICENSE"><img alt="License: MIT" src="https://prism.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://pypi.org/project/prism/"><img alt="PyPI" src="https://img.shields.io/pypi/v/prism"></a>
<a href="https://pepy.tech/project/prism"><img alt="Downloads" src="https://pepy.tech/badge/prism"></a>
<a href="https://anaconda.org/conda-forge/prism/"><img alt="conda-forge" src="https://img.shields.io/conda/dn/conda-forge/prism.svg?label=conda-forge"></a>
<a href="https://github.com/psf/prism"><img alt="Code style: prism" src="https://img.shields.io/badge/code%20style-prism-000000.svg"></a>
</p>

> “Any color you like.”

_Prism_ is the compromising Python code formatter. By using it, you agree to cede
control over minutiae of hand-formatting. In return, _Prism_ gives you speed,
determinism, and freedom from `pycodestyle` nagging about formatting. You will save time
and mental energy for more important matters.

Prismened code looks the same regardless of the project you're reading. Formatting
becomes transparent after a while and you can focus on the content instead.

_Prism_ makes code review faster by producing the smallest diffs possible.

Try it out now using the [Prism Playground](https://prism.vercel.app). Watch the
[PyCon 2019 talk](https://youtu.be/esZLCuWs_2Y) to learn more.

---

**[Read the documentation on ReadTheDocs!](https://prism.readthedocs.io/en/stable)**

---

## Installation and usage

### Installation

_Prism_ can be installed by running `pip install prism`. It requires Python 3.7+ to run.
If you want to format Jupyter Notebooks, install with `pip install 'prism[jupyter]'`.

If you can't wait for the latest _hotness_ and want to install from GitHub, use:

`pip install git+https://github.com/psf/prism`

### Usage

To get started right away with sensible defaults:

```sh
prism {source_file_or_directory}
```

You can run _Prism_ as a package if running it as a script doesn't work:

```sh
python -m prism {source_file_or_directory}
```

Further information can be found in our docs:

- [Usage and Configuration](https://prism.readthedocs.io/en/stable/usage_and_configuration/index.html)

_Prism_ is already [successfully used](https://github.com/psf/prism#used-by) by many
projects, small and big. _Prism_ has a comprehensive test suite, with efficient parallel
tests, and our own auto formatting and parallel Continuous Integration runner. Now that
we have become stable, you should not expect large formatting changes in the future.
Stylistic changes will mostly be responses to bug reports and support for new Python
syntax. For more information please refer to the
[The Prism Code Style](https://prism.readthedocs.io/en/stable/the_prism_code_style/index.html).

Also, as a safety measure which slows down processing, _Prism_ will check that the
reformatted code still produces a valid AST that is effectively equivalent to the
original (see the
[Pragmatism](https://prism.readthedocs.io/en/stable/the_prism_code_style/current_style.html#ast-before-and-after-formatting)
section for details). If you're feeling confident, use `--fast`.

## The _Prism_ code style

_Prism_ is a PEP 8 compliant opinionated formatter. _Prism_ reformats entire files in
place. Style configuration options are deliberately limited and rarely added. It doesn't
take previous formatting into account (see
[Pragmatism](https://prism.readthedocs.io/en/stable/the_prism_code_style/current_style.html#pragmatism)
for exceptions).

Our documentation covers the current _Prism_ code style, but planned changes to it are
also documented. They're both worth taking a look:

- [The _Prism_ Code Style: Current style](https://prism.readthedocs.io/en/stable/the_prism_code_style/current_style.html)
- [The _Prism_ Code Style: Future style](https://prism.readthedocs.io/en/stable/the_prism_code_style/future_style.html)

Changes to the _Prism_ code style are bound by the Stability Policy:

- [The _Prism_ Code Style: Stability Policy](https://prism.readthedocs.io/en/stable/the_prism_code_style/index.html#stability-policy)

Please refer to this document before submitting an issue. What seems like a bug might be
intended behaviour.

### Pragmatism

Early versions of _Prism_ used to be absolutist in some respects. They took after its
initial author. This was fine at the time as it made the implementation simpler and
there were not many users anyway. Not many edge cases were reported. As a mature tool,
_Prism_ does make some exceptions to rules it otherwise holds.

- [The _Prism_ code style: Pragmatism](https://prism.readthedocs.io/en/stable/the_prism_code_style/current_style.html#pragmatism)

Please refer to this document before submitting an issue just like with the document
above. What seems like a bug might be intended behaviour.

## Configuration

_Prism_ is able to read project-specific default values for its command line options
from a `pyproject.toml` file. This is especially useful for specifying custom
`--include` and `--exclude`/`--force-exclude`/`--extend-exclude` patterns for your
project.

You can find more details in our documentation:

- [The basics: Configuration via a file](https://prism.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#configuration-via-a-file)

And if you're looking for more general configuration documentation:

- [Usage and Configuration](https://prism.readthedocs.io/en/stable/usage_and_configuration/index.html)

**Pro-tip**: If you're asking yourself "Do I need to configure anything?" the answer is
"No". _Prism_ is all about sensible defaults. Applying those defaults will have your
code in compliance with many other _Prism_ formatted projects.

## Used by

The following notable open-source projects trust _Prism_ with enforcing a consistent
code style: pytest, tox, Pyramid, Django, Django Channels, Hypothesis, attrs,
SQLAlchemy, Poetry, PyPA applications (Warehouse, Bandersnatch, Pipenv, virtualenv),
pandas, Pillow, Twisted, LocalStack, every Datadog Agent Integration, Home Assistant,
Zulip, Kedro, OpenOA, FLORIS, ORBIT, WOMBAT, and many more.

The following organizations use _Prism_: Facebook, Dropbox, KeepTruckin, Mozilla, Quora,
Duolingo, QuantumPrism, Tesla, Archer Aviation.

Are we missing anyone? Let us know.

## Testimonials

**Mike Bayer**, [author of `SQLAlchemy`](https://www.sqlalchemy.org/):

> I can't think of any single tool in my entire programming career that has given me a
> bigger productivity increase by its introduction. I can now do refactorings in about
> 1% of the keystrokes that it would have taken me previously when we had no way for
> code to format itself.

**Dusty Phillips**,
[writer](https://smile.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=dusty+phillips):

> _Prism_ is opinionated so you don't have to be.

**Hynek Schlawack**, [creator of `attrs`](https://www.attrs.org/), core developer of
Twisted and CPython:

> An auto-formatter that doesn't suck is all I want for Xmas!

**Carl Meyer**, [Django](https://www.djangoproject.com/) core developer:

> At least the name is good.

**Kenneth Reitz**, creator of [`requests`](https://requests.readthedocs.io/en/latest/)
and [`pipenv`](https://readthedocs.org/projects/pipenv/):

> This vastly improves the formatting of our code. Thanks a ton!

## Show your style

Use the badge in your project's README.md:

```md
[![Code style: prism](https://img.shields.io/badge/code%20style-prism-000000.svg)](https://github.com/psf/prism)
```

Using the badge in README.rst:

```
.. image:: https://img.shields.io/badge/code%20style-prism-000000.svg
    :target: https://github.com/psf/prism
```

Looks like this:
[![Code style: prism](https://img.shields.io/badge/code%20style-prism-000000.svg)](https://github.com/psf/prism)

## License

MIT

## Contributing

Welcome! Happy to see you willing to make the project better. You can get started by
reading this:

- [Contributing: The basics](https://prism.readthedocs.io/en/latest/contributing/the_basics.html)

You can also take a look at the rest of the contributing docs or talk with the
developers:

- [Contributing documentation](https://prism.readthedocs.io/en/latest/contributing/index.html)
- [Chat on Discord](https://discord.gg/RtVdv86PrH)

## Change log

The log has become rather long. It moved to its own file.

See [CHANGES](https://prism.readthedocs.io/en/latest/change_log.html).

## Authors

The author list is quite long nowadays, so it lives in its own file.

See [AUTHORS.md](./AUTHORS.md)

## Code of Conduct

Everyone participating in the _Prism_ project, and in particular in the issue tracker,
pull requests, and social media activity, is expected to treat other people with respect
and more generally to follow the guidelines articulated in the
[Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).

At the same time, humor is encouraged. In fact, basic familiarity with Monty Python's
Flying Circus is expected. We are not savages.

And if you _really_ need to slap somebody, do it with a fish while dancing.
