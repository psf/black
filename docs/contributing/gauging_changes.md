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

```text
Usage: black-primer [OPTIONS]

  primer - prime projects for blackening... 🏴

Options:
  -c, --config PATH      JSON config file path  [default: /Users/cooper/repos/
                         black/src/black_primer/primer.json]

  --debug                Turn on debug logging  [default: False]
  -k, --keep             Keep workdir + repos post run  [default: False]
  -L, --long-checkouts   Pull big projects to test  [default: False]
  -R, --rebase           Rebase project if already checked out  [default:
                         False]

  -w, --workdir PATH     Directory path for repo checkouts  [default: /var/fol
                         ders/tc/hbwxh76j1hn6gqjd2n2sjn4j9k1glp/T/primer.20200
                         517125229]

  -W, --workers INTEGER  Number of parallel worker coroutines  [default: 2]
  -h, --help             Show this message and exit.
```
