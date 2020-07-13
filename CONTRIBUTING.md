# Contributing to _Black_

Welcome! Happy to see you willing to make the project better. Have you read the entire
[user documentation](https://black.readthedocs.io/en/latest/) yet?

## Bird's eye view

In terms of inspiration, _Black_ is about as configurable as _gofmt_. This is
deliberate.

Bug reports and fixes are always welcome! Please follow the
[issue template on GitHub](https://github.com/psf/black/issues/new) for best results.

Before you suggest a new feature or configuration knob, ask yourself why you want it. If
it enables better integration with some workflow, fixes an inconsistency, speeds things
up, and so on - go for it! On the other hand, if your answer is "because I don't like a
particular formatting" then you're not ready to embrace _Black_ yet. Such changes are
unlikely to get accepted. You can still try but prepare to be disappointed.

## Technicalities

Development on the latest version of Python is preferred. As of this writing it's 3.8.
You can use any operating system. I am using macOS myself and CentOS at work.

Install all development dependencies using:

```console
$ pipenv install --dev
$ pipenv shell
$ pre-commit install
```

If you haven't used `pipenv` before but are comfortable with virtualenvs, just run
`pip install pipenv` in the virtualenv you're already using and invoke the command above
from the cloned _Black_ repo. It will do the correct thing.

Before submitting pull requests, run lints and tests with:

```console
$ pre-commit run -a
$ python -m unittest
$ black-primer [-k -w /tmp/black_test_repos]
```

## black-primer

`black-primer` is used by CI to pull down well-known _Black_ formatted projects and see
if we get source code changes. It will error on formatting changes or errors. Please run
before pushing your PR to see if you get the actions you would expect from _Black_ with
your PR. You may need to change
[primer.json](https://github.com/psf/black/blob/master/src/black_primer/primer.json)
configuration for it to pass.

For more `black-primer` information visit the
[documentation](https://github.com/psf/black/blob/master/docs/black_primer.md).

## Hygiene

If you're fixing a bug, add a test. Run it first to confirm it fails, then fix the bug,
run it again to confirm it's really fixed.

If adding a new feature, add a test. In fact, always add a test. But wait, before adding
any large feature, first open an issue for us to discuss the idea first.

## Finally

Thanks again for your interest in improving the project! You're taking action when most
people decide to sit and watch.
