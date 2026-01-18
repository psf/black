# Gauging changes

A lot of the time, your change will affect formatting and/or performance. Quantifying
these changes is hard, so we have tooling to help make it easier.

It's recommended you evaluate the quantifiable changes your _Black_ formatting
modification causes before submitting a PR. Think about if the change seems disruptive
enough to cause frustration to projects that are already "Black-formatted".

## diff-shades

diff-shades is a tool that runs _Black_ across a list of open-source projects recording
the results. The main highlight feature of diff-shades is being able to compare two
revisions of _Black_. This is incredibly useful as it allows us to see what exact
changes will occur, say merging a certain PR.

For more information, please see the [diff-shades documentation][diff-shades].

### CI integration

diff-shades is also the tool behind the "diff-shades results comparing ..." comments on
PRs. The project has a GitHub Actions workflow that analyzes and compares two revisions
of _Black_ according to these rules:

|                       | Baseline revision               | Target revision              |
| --------------------- | ------------------------------- | ---------------------------- |
| On PRs                | latest commit on PR base branch | PR commit with `main` merged |
| On pushes (main only) | latest PyPI version             | the pushed commit            |

For pushes to main, there's only one analysis job named `preview-new-changes` where the
preview style is used for all projects.

For PRs they get one more analysis job: `assert-no-changes`. It's similar to
`preview-new-changes` but runs with the stable code style. It will fail if changes were
made. This makes sure code won't be reformatted again and again within the same year in
accordance to Black's stability policy.

Additionally for PRs, a PR comment will be posted embedding a summary previewing any
changes in both styles and links to further information. The next time the workflow is
triggered on the same PR, it'll update the pre-existing diff-shades comment.

```{note}
Jobs will only fail intentionally if a file failed to format while analyzing, or if
changes were made to the stable style. Otherwise a failure indicates a bug in the
workflow.
```

The workflow uploads several artifacts upon completion:

- HTML diffs (.html)
  - handy for pushes where there's no PR to post a comment
- The raw analyses (.json)
  - in case you want to do further analysis using the collected data locally
- `.preview.pr-comment.md` and `.stable.pr-comment.md` (if triggered by a PR)
  - used to generate the PR comment and shouldn't be downloaded

[diff-shades]: https://github.com/ichard26/diff-shades#readme
