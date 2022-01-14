# Gauging changes

A lot of the time, your change will affect formatting and/or performance. Quantifying
these changes is hard, so we have tooling to help make it easier.

It's recommended you evaluate the quantifiable changes your _Black_ formatting
modification causes before submitting a PR. Think about if the change seems disruptive
enough to cause frustration to projects that are already "black formatted".

## black-primer

`black-primer` is a tool built for CI (and humans) to have _Black_ `--check` a number of
Git accessible projects in parallel. (configured in `primer.json`) _(A PR will be
accepted to add Mercurial support.)_

### Run flow

- Ensure we have a `black` + `git` in PATH
- Load projects from `primer.json`
- Run projects in parallel with `--worker` workers (defaults to CPU count / 2)
  - Checkout projects
  - Run black and record result
  - Clean up repository checkout _(can optionally be disabled via `--keep`)_
- Display results summary to screen
- Default to cleaning up `--work-dir` (which defaults to tempfile schemantics)
- Return
  - 0 for successful run
  - \< 0 for environment / internal error
  - \> 0 for each project with an error

### Speed up runs 🏎

If you're running locally yourself to test black on lots of code try:

- Using `-k` / `--keep` + `-w` / `--work-dir` so you don't have to re-checkout the repo
  each run

### CLI arguments

```{program-output} black-primer --help

```

## diff-shades

diff-shades is a tool similar to black-primer, it also runs _Black_ across a list of Git
cloneable OSS projects recording the results. The intention is to eventually fully
replace black-primer with diff-shades as it's much more feature complete and supports
our needs better.

The main highlight feature of diff-shades is being able to compare two revisions of
_Black_. This is incredibly useful as it allows us to see what exact changes will occur,
say merging a certain PR. Black-primer's results would usually be filled with changes
caused by pre-existing code in Black drowning out the (new) changes we want to see. It
operates similarly to black-primer but crucially it saves the results as a JSON file
which allows for the rich comparison features alluded to above.

For more information, please see the [diff-shades documentation][diff-shades].

### CI integration

diff-shades is also the tool behind the "diff-shades results comparing ..." /
"diff-shades reports zero changes ..." comments on PRs. The project has a GitHub Actions
workflow which runs diff-shades twice against two revisions of _Black_ according to
these rules:

|                       | Baseline revision       | Target revision              |
| --------------------- | ----------------------- | ---------------------------- |
| On PRs                | latest commit on `main` | PR commit with `main` merged |
| On pushes (main only) | latest PyPI version     | the pushed commit            |

Once finished, a PR comment will be posted embedding a summary of the changes and links
to further information. If there's a pre-existing diff-shades comment, it'll be updated
instead the next time the workflow is triggered on the same PR.

The workflow uploads 3-4 artifacts upon completion: the two generated analyses (they
have the .json file extension), `diff.html`, and `.pr-comment-body.md` if triggered by a
PR. The last one is downloaded by the `diff-shades-comment` workflow and shouldn't be
downloaded locally. `diff.html` comes in handy for push-based or manually triggered
runs. And the analyses exist just in case you want to do further analysis using the
collected data locally.

Note that the workflow will only fail intentionally if while analyzing a file failed to
format. Otherwise a failure indicates a bug in the workflow.

```{tip}
Maintainers with write access or higher can trigger the workflow manually from the
Actions tab using the `workflow_dispatch` event. Simply select "diff-shades"
from the workflows list on the left, press "Run workflow", and fill in which revisions
and command line arguments to use.

Once finished, check the logs or download the artifacts for local use.
```

[diff-shades]: https://github.com/ichard26/diff-shades#readme
