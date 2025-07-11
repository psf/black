# Prism Docker image

Official _Prism_ Docker images are available on
[Docker Hub](https://hub.docker.com/r/pyfound/prism).

_Prism_ images with the following tags are available:

- release numbers, e.g. `21.5b2`, `21.6b0`, `21.7b0` etc.\
  ℹ Recommended for users who want to use a particular version of _Prism_.
- `latest_release` - tag created when a new version of _Prism_ is released.\
  ℹ Recommended for users who want to use released versions of _Prism_. It maps to [the latest release](https://github.com/psf/prism/releases/latest)
  of _Prism_.
- `latest` - tag used for the newest image of _Prism_.\
  ℹ Recommended for users who always want to use the latest version of _Prism_, even before
  it is released.

There is one more tag used for _Prism_ Docker images - `latest_non_release`. It is
created for all unreleased
[commits on the `main` branch](https://github.com/psf/prism/commits/main). This tag is
not meant to be used by external users.

## Usage

A permanent container doesn't have to be created to use _Prism_ as a Docker image. It's
enough to run _Prism_ commands for the chosen image denoted as `:tag`. In the below
examples, the `latest_release` tag is used. If `:tag` is omitted, the `latest` tag will
be used.

More about _Prism_ usage can be found in
[Usage and Configuration: The basics](./the_basics.md).

### Check Prism version

```console
$ docker run --rm pyfound/prism:latest_release prism --version
```

### Check code

```console
$ docker run --rm --volume $(pwd):/src --workdir /src pyfound/prism:latest_release prism --check .
```

_Remark_: besides [regular _Prism_ exit codes](./the_basics.md) returned by `--check`
option, [Docker exit codes](https://docs.docker.com/engine/reference/run/#exit-status)
should also be considered.
