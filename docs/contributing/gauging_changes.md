# Gauging changes

A lot of the time, your change will affect formatting and/or performance. Quantifying
these changes is hard, so we have tooling to help make it easier.

It's recommended you evaluate the quantifiable changes your _Black_ formatting
modification causes before submitting a PR. Think about if the change seems disruptive
enough to cause frustration to projects that are already "black formatted".

## black-primer

`black-primer` is an obsolete tool (now replaced with `diff-shades`) that was used to
gauge the impact of changes in _Black_ on open-source code. It is no longer used
internally and will be removed from the _Black_ repository in the future.

## diff-shades

diff-shades is a tool that runs _Black_ across a list of Git cloneable OSS projects
recording the results. The main highlight feature of diff-shades is being able to
compare two revisions of _Black_. This is incredibly useful as it allows us to see what
exact changes will occur, say merging a certain PR.

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
have the .json file extension), `diff.html`, and `.pr-comment.json` if triggered by a
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
