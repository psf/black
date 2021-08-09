# Black Docker image

Official _Black_ Docker images are available on Docker Hub:
https://hub.docker.com/r/pyfound/black

From end-user perspective the following tags are used for _Black_ images:

- `latest` - tag used for the newest image of _Black_.\
  ℹ Recommended for users who always want to use the latest version of _Black_.
- `latest_release` - tag used for image created when new version of _Black_ is
  released.\
  ℹ Recommended for users who want to use released versions of _Black_. It maps to [the latest release](https://github.com/psf/black/releases/latest)
  of _Black_.
- release numbers, e.g. `21.5b2`, `21.6b0`, `21.7b0` etc.\
  ℹ Recommended for users who want to use particular version of _Black_.

There is one more tag used for _Black_ Docker images - `latest_non_release`. It is
created for all, still not released
[commits of `main` branch](https://github.com/psf/black/commits/main). It's more related
to software life-cycle, that targeted for end-users.

## Usage

Permanent container doesn't have to be created for using _Black_ as Docker image. It's
enough to run _Black_ commands for chosen image denoted as `:tag`. In examples below
`latest_release` tag is used. If `:tag` is omitted, `latest` tag will be used.

More about _Black_ usage can be found in
[Usage and Configuration: The basics](./the_basics.md).

### Check Black version

```console
$ docker run --rm pyfound/black:latest_release black --version
```

### Check code

```console
$ docker run --rm --volume $(pwd):/src --workdir /src pyfound/black:latest_release black --check .
```

_Remark_: besides [regular _Black_ exit codes](./the_basics.md) returned by `--check`
option, [Docker exit codes](https://docs.docker.com/engine/reference/run/#exit-status)
should also be considered.
