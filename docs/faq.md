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

## Why is my file not formatted?

Most likely because it is ignored in `.gitignore` or excluded with configuration. See
[file collection and discovery](usage_and_configuration/file_collection_and_discovery.md)
for details.

## Why are Flake8's E203 and W503 violated?

Because they go against PEP 8. E203 falsely triggers on list
[slices](the_black_code_style/current_style.md#slices), and adhering to W503 hinders
readability because operators are misaligned. Disable W503 and enable the
disabled-by-default counterpart W504. E203 should be disabled while changes are still
[discussed](https://github.com/PyCQA/pycodestyle/issues/373).

## Does Black support Python 2?

For formatting, yes! [Install](getting_started.md#installation) with the `python2` extra
to format Python 2 files too! There are no current plans to drop support, but most
likely it is bound to happen. Sometime. Eventually. In terms of running _Black_ though,
Python 3.6 or newer is required.

## Why does my linter or typechecker complain after I format my code?

Some linters and other tools use magical comments (e.g., `# noqa`, `# type: ignore`) to
influence their behavior. While Black does its best to recognize such comments and leave
them in the right place, this detection is not and cannot be perfect. Therefore, you'll
sometimes have to manually move these comments to the right place after you format your
codebase with _Black_.
