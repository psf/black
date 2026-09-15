# Release process

_Black_'s release process has been standardized and automated. This document explains
what to expect and how to release _Black_ using said automation.

## Release cadence

**We aim to release whatever is on `main` every 1-2 months.** This ensures merged
improvements and bugfixes are shipped to users reasonably quickly, while not massively
fracturing the userbase with too many versions. This also keeps the workload on
maintainers consistent and predictable.

If there's not much new on `main` to justify a release, it's acceptable to skip a
month's release. Ideally January releases should not be skipped, since the first release
in a new calendar year may make changes to the _stable_ style, as per our
[stability policy](labels/stability-policy). While the policy applies to the first
release (instead of only January releases), confining changes to the stable style to
January will keep things predictable (and nicer) for users.

Unless there is a serious regression or bug that requires immediate patching, **there
should not be more than one release per month**. While version numbers are cheap,
releases require a maintainer to commit not only to the actual cutting of a release, but
also to deal with the potential fallout post-release. Releasing more frequently than
monthly nets rapidly diminishing returns.

## Cutting a release

**You must have `write` permissions for the _Black_ repository to cut a release.**

The 10,000-foot view of the release process is that you trigger a workflow to create a
PR automating the release chores. Then, merge it, triggering
[release automation](#release-workflows) that builds all release artifacts and publishes
them to the various platforms we publish to.

Start here for prereleases as well. Run "prepare release" against `main` as described
before stabilizing preview features or making other prerelease changes. The appropriate
times to do those are included in the instructions below.

To cut a release:

1. **Run [the "prepare release" workflow][prepare-release-workflow].** Make sure to
   leave the main branch selected. This will create a PR automating most of the needed
   changes.
   - For stable versions, the workflow will automatically determine the next version
     number. Leave the `Version_Override` input empty.
     - For reference, _Black_ follows the [CalVer] versioning standard using the
       `YY.M.N` format.
     - Unless there already has been a release during the month, `N` should be `0`.
     - Example: the first release in January 2026 is `26.1.0`.
   - If you're releasing a prerelease, specify **the expected stable release version**
     in the box provided (not the version of the prerelease). The prerelease version
     will be determined automatically, following these rules:
     - Prereleases use the `YY.MMaN` format.
     - The first alpha should start `N` at `1` (not `0`).
     - Example: the first alpha released in December 2025 and to be stabilized in
       January 2026 is `26.1a1`, but `Version_Override` should be set to `26.1.0`.

1. You will be auto-assigned to the created PR. **Check the changelog diff in the
   description and copyedit `CHANGES.md`.** The CI will update it after each push, so
   double-check it again before you merge. Things to check include:
   - Make sure nothing was put into the wrong version or section, particularly things
     that you might want to move to "Highlights"
   - Rephrase unclear or unnecessarily detailed entries (a sentence or two is probably
     plenty for most changes)
   - Remove duplicates, fix typos, and reorder entries if needed

1. **If you're releasing a prerelease or major version, commit the changes unique to
   it** to the PR branch. If you make any changes that should have a changelog entry,
   remember to add one!

   If you're releasing a major version (or a prerelease for one), there are some
   specific additional changes to make at this point:
   - Bump `wcwidth` to the latest version and run `scripts/make_width_table.py`
   - Find any references to the old version and bump them (references to minor versions
     are auto-bumped, so you don't need to check when releasing minor versions)

1. **Wait for CI to pass on the PR, and fix any failures.**
   - If CI does not pass, **stop** and investigate the failure(s) as we'd generally want
     to fix failing CI before cutting a release.

1. **To cut a stable release, merge the PR once everything looks good.** If you're
   cutting a prerelease, **do not merge it**, and instead [run the "cut release"
   workflow][cut-release-workflow] manually. **Make sure to select the
   `ci/prepare-release/<verson>` branch**, where `<version>` is the stable version
   you're preparing. You can release multiple prereleases from the same PR by running
   "cut release" multiple times after any desired changes.

1. **Make sure CI passes.** At this point, you're basically done, but it's good practice
   to [watch and verify that all the release workflows pass][black-actions], though
   GitHub may notify you anyway if something fails.
   - If something fails, don't panic. Please go read the respective workflow's logs and
     configuration file to reverse-engineer your way to a solution.
   - If the failure is in the "cut release" workflow before "update stable" runs, you're
     able to commit a fix to `main` and rerun it manually with no issues. Again, run it
     on the `main` branch for stable releases or the `ci/prepare-release/<verson>`
     branch for prereleases.
   - If a different workflow fails, the release can't be fully reverted at this point.
     Determine the best course of action according to what failed and the necessary
     changes.
   - After a stable release is published, the CI will also create a PR to add the next
     version's changelog. Once everything passes, merge it.

Congratulations! You've successfully cut a new release of _Black_. Go stand up and take
a break, you deserve it.

```{important}
Once the release artifacts are published, you may see new issues being filed indicating
regressions. While regressions are not great, they don't automatically mean a hotfix
release is warranted. Unless the regressions are serious and impact many users, a hotfix
release is probably unnecessary. In the end, use your best judgment and ask other
maintainers for their thoughts.
```

## Release workflows

All of _Black_'s release automation uses [GitHub Actions]. All workflows are therefore
configured using YAML files in the `.github/workflows` directory of the _Black_
repository. They are triggered at various points in the release process detailed above.

### prepare release

This workflow is manually run as the first step in the release process. It handles many
of the initial chores before releasing.

#### create

This job runs `scripts/release.py` to clean up CHANGES.md and bump most references to
old _Black_ versions, then creates a PR with the changes for your review. The PR
creation is authenticated in order to trigger test CI.

```{note}
_Currently this workflow uses a GitHub API Token associated with @TODO's account._
```

#### update

This job runs after `create` and after each subsequent push to the PR. It updates the
changelog diff in the PR description.

### cut release

This workflow runs when the changelog PR is merged (or when manually triggered, in the
case of prereleases or reruns after a failure). It creates and publishes a release,
which triggers the other release workflows, then completes final post-release chores.

#### release

This job determines if the release should be a prerelease (if the workflow is run on a
branch other than `main`). It then creates a draft release for the next step.

#### build-binaries (…)

These matrix jobs build native executables for multiple platforms using [PyInstaller].
This allows people to download the executable for their platform and run _Black_ without
a Python runtime installed.

The created binaries are stored on the associated draft GitHub Release for download.
Note that we use [GitHub's immutable releases][immutable-releases], preventing assets or
tags from being modified once the release is published as a security measure.

#### update-stable

This job marks the release as published. This is authenticated in order to trigger
further release automation. Then, only if the release was stable, it updates the
`stable` branch by force pushing it to the most recent tag.

```{note}
_Currently this workflow uses a GitHub API Token associated with @TODO's account._
```

#### new-changelog

This job opens a new PR to add the "Unreleased" section back to the changelog. The PR is
not auto-merged to allow the releaser time to make sure all the release workflows
succeed. The PR creation is authenticated in order to trigger test CI.

```{note}
_Currently this workflow uses a GitHub API Token associated with @TODO's account._
```

### build and publish

This is our main workflow, triggered when the release is published. It builds an [sdist]
and [wheels] to upload to PyPI, where the vast majority of users download _Black_ from.

It also runs as a test dry run on each PR and push to `main` (without publishing
anything to PyPI).

#### sdist + pure wheel

This single job builds the sdist and pure Python wheel (i.e., a wheel that only contains
Python code) using [Hatch]. These artifacts are general-purpose and can be used on
basically any platform supported by Python.

#### generate wheels matrix / mypyc wheels (…)

We use [mypyc] to compile _Black_ into a CPython C extension for significantly improved
performance. Wheels built with mypyc are platform and Python version specific.
[Supported platforms are documented in the FAQ](labels/mypyc-support).

These matrix jobs use [cibuildwheel] which handles the complicated task of building C
extensions for many environments for us. It uses a matrix to build each platform in
parallel (as noted in the job name in parentheses).

#### publish-hatch / publish-mypyc

These jobs upload the built sdist and all wheels to PyPI using [Trusted Publishing].
This step does not run on PRs or pushes to `main`.

### docker

This workflow uses Docker Buildx to build and push `arm64` and `amd64`/`x86_64` builds
of the official _Black_ Docker image to Docker Hub.

This also runs on each push to `main`.

```{note}
_Currently this workflow uses a Docker API Token associated with @cooperlees's account._
```

[black-actions]: https://github.com/psf/black/actions
[calver]: https://calver.org
[cibuildwheel]: https://cibuildwheel.readthedocs.io/
[cut-release-workflow]: https://github.com/psf/black/actions/workflows/cut_release.yml
[github actions]: https://github.com/features/actions
[hatch]: https://hatch.pypa.io/latest/
[immutable-releases]:
  https://docs.github.com/code-security/concepts/supply-chain-security/immutable-releases
[mypyc]: https://mypyc.readthedocs.io/en/stable/
[prepare-release-workflow]:
  https://github.com/psf/black/actions/workflows/prepare_release.yml
[pyinstaller]: https://www.pyinstaller.org/
[sdist]:
  https://packaging.python.org/en/latest/glossary/#term-source-distribution-or-sdist
[trusted publishing]: https://docs.pypi.org/trusted-publishers/
[wheels]: https://packaging.python.org/en/latest/glossary/#term-wheel
