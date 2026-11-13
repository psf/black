# Introducing _Black_ to your project

## Tips for existing projects

There is no single way to introduce _Black_ to an existing project. The right approach
depends on the size of the codebase, active development, and the team's review workflow.
The following tips can help keep the change manageable.

Agreeing on which files to format and recording options (such as target Python versions
and line length) in `pyproject.toml` can make the initial reformat easier to review.
Pinning the same _Black_ version in local development and CI also helps contributors
produce consistent results.

If the project already has established string conventions, using
`--skip-string-normalization` can reduce churn during the initial adoption. Treat this
as an adoption aid rather than a recommended default for new projects, where _Black_'s
standard string normalization keeps formatting consistent.

Running the project's tests before and after formatting helps check for unexpected
changes. Keeping the formatting in its own commit, without refactors or behavior
changes, makes review and future history easier to follow. A single reformat may suit a
small project; for a larger one, formatting one directory or package at a time may be
easier to coordinate.

To keep new changes formatted, consider adding `black --check .` to CI and using the
{doc}`pre-commit integration </integrations/pre-commit>` for local feedback.
Configuration, formatting, and enforcement can be reviewed together or in separate pull
requests. If you want to ignore the formatting commit in `git blame`, choose a merge
method that preserves that commit separately from other changes. Separate pull requests
are one option for projects that use squash merges.

### Coordinating active branches

A repository-wide formatting commit can conflict with long-running branches that edit
the same lines. Announcing the planned merge time can help contributors coordinate
changes around it. Once the formatting commit is on the target branch, contributors can
update their branch, resolve any semantic conflicts, and run _Black_ over the result.
The final diff against the newly formatted target branch will then mostly contain the
intended code changes.

Avoid combining the reformat with automatic conflict strategies that always choose one
side: they can silently discard real changes. For especially busy repositories, merging
small or nearly complete branches before the rollout can reduce the number of conflicts
considerably.

## Avoiding ruining git blame

A long-standing argument against moving to automated code formatters like _Black_ is
that the migration will clutter up the output of `git blame`. This was a valid argument,
but since Git version 2.23, Git natively supports
[ignoring revisions in blame](https://git-scm.com/docs/git-blame#Documentation/git-blame.txt---ignore-revltrevgt)
with the `--ignore-rev` option. You can also pass a file listing the revisions to ignore
using the `--ignore-revs-file` option. The changes made by the revision will be ignored
when assigning blame. Lines modified by an ignored revision will be blamed on the
previous revision that modified those lines.

So when migrating your project's code style to _Black_, reformat everything and commit
the changes (preferably in one massive commit). Then put the full 40 characters commit
identifier(s) into a file usually called `.git-blame-ignore-revs` at the root of your
project directory.

```text
# Migrate code style to Black
5b4ab991dede475d393e9d69ec388fd6bd949699
```

Afterwards, you can pass that file to `git blame` and see clean and meaningful blame
information.

```console
$ git blame important.py --ignore-revs-file .git-blame-ignore-revs
7a1ae265 (John Smith 2019-04-15 15:55:13 -0400 1) def very_important_function(text, file):
abdfd8b0 (Alice Doe  2019-09-23 11:39:32 -0400 2)     text = text.lstrip()
7a1ae265 (John Smith 2019-04-15 15:55:13 -0400 3)     with open(file, "r+") as f:
7a1ae265 (John Smith 2019-04-15 15:55:13 -0400 4)         f.write(formatted)
```

You can even configure `git` to automatically ignore revisions listed in a file on every
call to `git blame`.

```console
$ git config blame.ignoreRevsFile .git-blame-ignore-revs
```

**The one caveat is that some online Git-repositories do not yet support ignoring
revisions using their native blame UI.** So blame information will be cluttered with a
reformatting commit on those platforms. However,
[GitHub](https://docs.github.com/en/repositories/working-with-files/using-files/viewing-a-file#ignore-commits-in-the-blame-view)
and
[GitLab (since version 17.10)](https://about.gitlab.com/releases/2025/03/20/gitlab-17-10-released/#ignore-specific-revisions-in-git-blame)
both support `.git-blame-ignore-revs` in blame views by default.
