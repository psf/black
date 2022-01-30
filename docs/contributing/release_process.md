# Release process

_Black_ has had a lot of work automating its release process. This document sets out to
explain what everything does and how to release _Black_ using said automation.

## Cutting a Release

To cut a release, you must be a _Black_ maintainer with `GitHub Release` creation
access. Using this access, the release process is:

1. Cut a new PR editing `CHANGES.md` and the docs to version the latest changes
   1. Remove any empty sections for the current release
   2. Add a new empty template for the next release (template below)
   3. Example PR: [#2616](https://github.com/psf/black/pull/2616)
   4. Example title: `Update CHANGES.md for XX.X release`
2. Once the release PR is merged ensure all CI passes
   1. If not, ensure there is an Issue open for the cause of failing CI (generally we'd
      want this fixed before cutting a release)
3. Open `CHANGES.md` and copy the _raw markdown_ of the latest changes to use in the
   description of the GitHub Release.
4. Go and [cut a release](https://github.com/psf/black/releases) using the GitHub UI so
   that all workflows noted below are triggered.
   1. The release version and tag should be the [CalVer](https://calver.org) version
      _Black_ used for the current release e.g. `21.6` / `21.5b1`
   2. _Black_ uses [setuptools scm](https://pypi.org/project/setuptools-scm/) to pull
      the current version for the package builds and release.
5. Once the release is cut, you're basically done. It's a good practice to go and watch
   to make sure all the [GitHub Actions](https://github.com/psf/black/actions) pass,
   although you should receive an email to your registered GitHub email address should
   one fail.
   1. You should see all the release workflows and lint/unittests workflows running on
      the new tag in the Actions UI

If anything fails, please go read the respective action's log output and configuration
file to reverse engineer your way to a fix/soluton.

## Changelog template

Use the following template for a clean changelog after the release:

```
## Unreleased

### Highlights

<!-- Include any especially major or disruptive changes here -->

### Style

<!-- Changes that affect Black's style -->

### _Blackd_

<!-- Changes to blackd -->

### Configuration

<!-- Changes to how Black can be configured -->

### Documentation

<!-- Major changes to documentation and policies. Small docs changes
     don't need a changelog entry. -->

### Integrations

<!-- For example, Docker, GitHub Actions, pre-commit, editors -->

### Output

<!-- Changes to Black's terminal output and error messages -->

### Packaging

<!-- Changes to how Black is packaged, such as dependency requirements -->

### Parser

<!-- Changes to the parser or to version autodetection -->

### Performance

<!-- Changes that improve Black's performance. -->

```

## Release workflows

All _Blacks_'s automation workflows use GitHub Actions. All workflows are therefore
configured using `.yml` files in the `.github/workflows` directory of the _Black_
repository.

Below are descriptions of our release workflows.

### Docker

This workflow uses the QEMU powered `buildx` feature of docker to upload a `arm64` and
`amd64`/`x86_64` build of the official _Black_ docker image™.

- Currently this workflow uses an API Token associated with @cooperlees account

### pypi_upload

This workflow builds a Python
[sdist](https://docs.python.org/3/distutils/sourcedist.html) and
[wheel](https://pythonwheels.com) using the latest
[setuptools](https://pypi.org/project/setuptools/) and
[wheel](https://pypi.org/project/wheel/) modules.

It will then use [twine](https://pypi.org/project/twine/) to upload both release formats
to PyPI for general downloading of the _Black_ Python package. This is where
[pip](https://pypi.org/project/pip/) looks by default.

- Currently this workflow uses an API token associated with @ambv's PyPI account

### Upload self-contained binaries

This workflow builds self-contained binaries for multiple platforms. This allows people
to download the executable for their platform and run _Black_ without a
[Python Runtime](https://wiki.python.org/moin/PythonImplementations) installed.

The created binaries are attached/stored on the associated
[GitHub Release](https://github.com/psf/black/releases) for download over _IPv4 only_
(GitHub still does not have IPv6 access 😢).

## Moving the `stable` tag

_Black_ provides a stable tag for people who want to move along as _Black_ developers
deem the newest version reliable. Here the _Black_ developers will move once the release
has been problem free for at least ~24 hours from release. Given the large _Black_
userbase we hear about bad bugs quickly. We do strive to continually improve our CI too.

### Tag moving process

#### stable

From a rebased `main` checkout:

1. `git tag -f stable VERSION_TAG`
   1. e.g. `git tag -f stable 21.5b1`
1. `git push --tags -f`
