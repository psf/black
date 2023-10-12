# Ways to install Black

There are several ways you can install _Black_.

## Install from PyPI

To install the latest release of _Black_ from [PyPI] (Requires Python 3.8+), use:

`pip install black`

A _Black_ release currently offers three types of artifacts via PyPI, as outlined in the
[Release Process]:

1. The source distribution of the release
2. Generic Python wheel, meant for use on any Python supported platform
3. Platform and Python version specific wheels that offer significantly improved
   performance, compiled using [mypyc]

By default, `pip` will prefer a compatible wheel and revert to the source distribution
if no such wheels are found, as outlined in [Python documentation].

## Install from GitHub

To install the latest version of _Black_ from GitHub, use:

`pip install git+https://github.com/psf/black`

## Get native binaries from GitHub

[GitHub Releases] for _Black_ contain self-contained, native binaries for multiple
platforms (built using PyInstaller). This allows you to download the executable for your
platform and run _Black_ without a Python runtime installed.

## Black Docker images

Official _Black_ Docker images are available on [Docker Hub]. For more information,
check the [Black Docker image] section.

[PyPI]: https://pypi.org/project/black/
[Release Process]: ./../contributing/release_process
[mypyc]: https://mypyc.readthedocs.io/
[Python documentation]:
  https://packaging.python.org/en/latest/tutorials/installing-packages/#source-distributions-vs-wheels
[GitHub Releases]: https://github.com/psf/black/releases
[Docker Hub]: https://hub.docker.com/r/pyfound/black
[Black Docker image]: ./black_docker_image
