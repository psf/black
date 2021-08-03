# Black Docker image

Official _Black_ Docker images are available on Docker Hub:
https://hub.docker.com/r/pyfound/black

Following tags are used for _Black_ images:

- `latest` - tag used for either
  [the latest commit of `main` branch](https://github.com/psf/black/commits/main) or
  [the latest release](https://github.com/psf/black/releases/latest)
- `latest_release` - tag used for
  [the latest release](https://github.com/psf/black/releases/latest)
- `latest_non_release` - tag used for
  [the latest commit of `main` branch](https://github.com/psf/black/commits/main)
- release numbers, e.g. `21.5b2`, `21.6b0`, `21.7b0` etc.

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
should be also considered.
