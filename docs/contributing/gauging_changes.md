# Gauging changes

A lot of the time, your change will affect formatting and/or performance. Quantifying
these changes is hard, so we have tooling to help make it easier.

It's recommended you evaluate the quantifiable changes your _Black_ formatting
modification causes before submitting a PR. Think about if the change seems disruptive
enough to cause frustration to projects that are already "black formatted".

## diff-shades

diff-shades is a tool that runs _Black_ across a list of open-source projects recording
the results. The main highlight feature of diff-shades is being able to compare two
revisions of _Black_. This is incredibly useful as it allows us to see what exact
changes will occur, say merging a certain PR.

For more information, please see the [diff-shades documentation][diff-shades].

### CI integration

diff-shades is also the tool behind the "diff-shades results comparing ..." /
"diff-shades reports zero changes ..." comments on PRs. The project has a GitHub Actions
workflow that analyzes and compares two revisions of _Black_ according to these rules:

|                       | Baseline revision       | Target revision              |
| --------------------- | ----------------------- | ---------------------------- |
| On PRs                | latest commit on `main` | PR commit with `main` merged |
| On pushes (main only) | latest PyPI version     | the pushed commit            |

For pushes to main, there's only one analysis job named `preview-changes` where the
preview style is used for all projects.

For PRs they get one more analysis job: `assert-no-changes`. It's similar to
`preview-changes` but runs with the stable code style. It will fail if changes were
made. This makes sure code won't be reformatted again and again within the same year in
accordance to Black's stability policy.

Additionally for PRs, a PR comment will be posted embedding a summary of the preview
changes and links to further information. If there's a pre-existing diff-shades comment,
it'll be updated instead the next time the workflow is triggered on the same PR.

```{note}
The `preview-changes` job will only fail intentionally if while analyzing a file failed to
format. Otherwise a failure indicates a bug in the workflow.
```

The workflow uploads several artifacts upon completion:

- The raw analyses (.json)
- HTML diffs (.html)
- `.pr-comment.json` (if triggered by a PR)

The last one is downloaded by the `diff-shades-comment` workflow and shouldn't be
downloaded locally. The HTML diffs come in handy for push-based where there's no PR to
post a comment. And the analyses exist just in case you want to do further analysis
using the collected data locally.

[diff-shades]: https://github.com/ichard26/diff-shades#readme
