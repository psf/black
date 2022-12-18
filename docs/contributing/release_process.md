# Release process

_Black_ has had a lot of work done into standardizing and automating its release
process. This document sets out to explain how everything works and how to release
_Black_ using said automation.

## Release cadence

**We aim to release whatever is on `main` every 1-2 months.** This ensures merged
improvements and bugfixes are shipped to users reasonably quickly, while not massively
fracturing the user-base with too many versions. This also keeps the workload on
maintainers consistent and predictable.

If there's not much new on `main` to justify a release, it's acceptable to skip a
month's release. Ideally January releases should not be skipped because as per our
[stability policy](labels/stability-policy), the first release in a new calendar year
may make changes to the _stable_ style. While the policy applies to the first release
(instead of only January releases), confining changes to the stable style to January
will keep things predictable (and nicer) for users.

Unless there is a serious regression or bug that requires immediate patching, **there
should not be more than one release per month**. While version numbers are cheap,
releases require a maintainer to both commit to do the actual cutting of a release, but
also to be able to deal with the potential fallout post-release. Releasing more
frequently than monthly nets rapidly diminishing returns.

## Cutting a release

**You must have `write` permissions for the _Black_ repository to cut a release.**

The 10,000 foot view of the release process is that you prepare a release PR and then
publish a [GitHub Release]. This triggers [release automation](#release-workflows) that
builds all release artifacts and publishes them to the various platforms we publish to.

To cut a release:

1. Determine the release's version number
   - **_Black_ follows the [CalVer] versioning standard using the `YY.M.N` format**
     - So unless there already has been a release during this month, `N` should be `0`
   - Example: the first release in January, 2022 → `22.1.0`
1. File a PR editing `CHANGES.md` and the docs to version the latest changes
   1. Replace the `## Unreleased` header with the version number
   1. Remove any empty sections for the current release
   1. (_optional_) Read through and copy-edit the changelog (eg. by moving entries,
      fixing typos, or rephrasing entries)
   1. Add a new empty template for the next release above
      ([template below](#changelog-template))
   1. Update references to the latest version in
      {doc}`/integrations/source_version_control` and
      {doc}`/usage_and_configuration/the_basics`
   - Example PR: [GH-3139]
1. Once the release PR is merged, wait until all CI passes
   - If CI does not pass, **stop** and investigate the failure(s) as generally we'd want
     to fix failing CI before cutting a release
1. [Draft a new GitHub Release][new-release]
   1. Click `Choose a tag` and type in the version number, then select the
      `Create new tag: YY.M.N on publish` option that appears
   1. Verify that the new tag targets the `main` branch
   1. You can leave the release title blank, GitHub will default to the tag name
   1. Copy and paste the _raw changelog Markdown_ for the current release into the
      description box
1. Publish the GitHub Release, triggering [release automation](#release-workflows) that
   will handle the rest
1. At this point, you're basically done. It's good practice to go and [watch and verify
   that all the release workflows pass][black-actions], although you will receive a
   GitHub notification should something fail.
   - If something fails, don't panic. Please go read the respective workflow's logs and
     configuration file to reverse-engineer your way to a fix/solution.

Congratulations! You've successfully cut a new release of _Black_. Go and stand up and
take a break, you deserve it.

```{important}
Once the release artifacts reach PyPI, you may see new issues being filed indicating
regressions. While regressions are not great, they don't automatically mean a hotfix
release is warranted. Unless the regressions are serious and impact many users, a hotfix
release is probably unnecessary.

In the end, use your best judgement and ask other maintainers for their thoughts.
```

### Changelog template

Use the following template for a clean changelog after the release:

```
## Unreleased

### Highlights

<!-- Include any especially major or disruptive changes here -->

### Stable style

<!-- Changes that affect Black's stable style -->

### Preview style

<!-- Changes that affect Black's preview style -->

### Configuration

<!-- Changes to how Black can be configured -->

### Packaging

<!-- Changes to how Black is packaged, such as dependency requirements -->

### Parser

<!-- Changes to the parser or to version autodetection -->

### Performance

<!-- Changes that improve Black's performance. -->

### Output

<!-- Changes to Black's terminal output and error messages -->

### _Blackd_

<!-- Changes to blackd -->

### Integrations

<!-- For example, Docker, GitHub Actions, pre-commit, editors -->

### Documentation

<!-- Major changes to documentation and policies. Small docs changes
     don't need a changelog entry. -->
```

## Release workflows

All of _Black_'s release automation uses [GitHub Actions]. All workflows are therefore
configured using YAML files in the `.github/workflows` directory of the _Black_
repository.

They are triggered by the publication of a [GitHub Release].

Below are descriptions of our release workflows.

### Publish to PyPI

This is our main workflow. It builds an [sdist] and [wheels] to upload to PyPI where the
vast majority of users will download Black from. It's divided into three job groups:

#### sdist + pure wheel

This single job builds the sdist and pure Python wheel (i.e., a wheel that only contains
Python code) using [build] and then uploads them to PyPI using [twine]. These artifacts
are general-purpose and can be used on basically any platform supported by Python.

#### mypyc wheels (…)

We use [mypyc] to compile _Black_ into a CPython C extension for significantly improved
performance. Wheels built with mypyc are platform and Python version specific.
[Supported platforms are documented in the FAQ](labels/mypyc-support).

These matrix jobs use [cibuildwheel] which handles the complicated task of building C
extensions for many environments for us. Since building these wheels is slow, there are
multiple mypyc wheels jobs (hence the term "matrix") that build for a specific platform
(as noted in the job name in parentheses).

Like the previous job group, the built wheels are uploaded to PyPI using [twine].

#### Update stable branch

So this job doesn't _really_ belong here, but updating the `stable` branch after the
other PyPI jobs pass (they must pass for this job to start) makes the most sense. This
saves us from remembering to update the branch sometime after cutting the release.

- _Currently this workflow uses an API token associated with @ambv's PyPI account_

### Publish executables

This workflow builds native executables for multiple platforms using [PyInstaller]. This
allows people to download the executable for their platform and run _Black_ without a
[Python runtime](https://wiki.python.org/moin/PythonImplementations) installed.

The created binaries are stored on the associated GitHub Release for download over _IPv4
only_ (GitHub still does not have IPv6 access 😢).

### docker

This workflow uses the QEMU powered `buildx` feature of Docker to upload an `arm64` and
`amd64`/`x86_64` build of the official _Black_ Docker image™.

- _Currently this workflow uses an API Token associated with @cooperlees account_

```{note}
This also runs on each push to `main`.
```

[black-actions]: https://github.com/psf/black/actions
[build]: https://pypa-build.readthedocs.io/
[calver]: https://calver.org
[cibuildwheel]: https://cibuildwheel.readthedocs.io/
[gh-3139]: https://github.com/psf/black/pull/3139
[github actions]: https://github.com/features/actions
[github release]: https://github.com/psf/black/releases
[new-release]: https://github.com/psf/black/releases/new
[mypyc]: https://mypyc.readthedocs.io/
[mypyc-platform-support]:
  /faq.html#what-is-compiled-yes-no-all-about-in-the-version-output
[pyinstaller]: https://www.pyinstaller.org/
[sdist]:
  https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist
[twine]: https://github.com/features/actions
[wheels]: https://packaging.python.org/en/latest/glossary/#term-Wheel
