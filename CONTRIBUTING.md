# Contributing to _Black_

Welcome future contributor! We're happy to see you willing to make the project better.

If you aren't familiar with _Black_, or are looking for documentation on something
specific, the [user documentation](https://black.readthedocs.io/en/latest/) is the best
place to look.

For getting started on contributing, please read the
[contributing documentation](https://black.readthedocs.org/en/latest/contributing/) for
all you need to know.

## Thank you, and we look forward to your contributions!

## CI: `ci: build all wheels` label

Black does not build wheels for every supported platform on every pull request because
the full wheel matrix is large and expensive. In cases where a contributor or maintainer
needs to test the full wheel build (for example, to reproduce platform-specific
failures), the `ci: build all wheels` label can be applied to a pull request.

### Important: Build will NOT trigger immediately after labeling

Due to how GitHub Actions processes events, simply adding the label does **not** start
the wheel build workflow. The full wheel build will only run **after at least one new
commit is pushed to the pull request**.

To trigger a build manually, you can push an empty commit:

```bash
git commit --allow-empty -m "trigger full wheels build" && git push
```
