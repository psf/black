# Introducing _Black_ to your project

## Planning the rollout

Treat the initial reformat as a mechanical change. Before running _Black_, agree on the
files that it should format and commit the project's configuration (such as the target
Python versions and line length) to `pyproject.toml`. Pinning the same _Black_ version
in local development and CI also prevents contributors from producing different
results during the rollout.

Run the project's tests before and after formatting. Commit the formatting by itself,
without refactors or other behavior changes, so that reviewers can verify it quickly
and future history remains easy to follow. If formatting the entire repository at once
is impractical, split the rollout along clear directory or package boundaries and avoid
editing those areas for other reasons until their formatting commit lands.

Enable enforcement as soon as the formatting commit is merged. For example, add
`black --check .` to CI and use the
{doc}`pre-commit integration </integrations/source_version_control>` for local
feedback. Keeping configuration and enforcement in the same pull request prevents new
unformatted changes from accumulating during the transition.

### Coordinating active branches

A repository-wide formatting commit will conflict with long-running branches that
edit the same lines. Announce the planned merge time and ask contributors to minimize
large changes around it. Once the formatting commit is on the target branch,
contributors should update their branch, resolve any semantic conflicts, and run
_Black_ over the result. The final diff against the newly formatted target branch will
then mostly contain the intended code changes.

Avoid combining the reformat with automatic conflict strategies that always choose
one side: they can silently discard real changes. For especially busy repositories,
merging small or nearly complete branches before the rollout can reduce the number of
conflicts considerably.

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
