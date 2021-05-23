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
