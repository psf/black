# Ways to install Black

There are several ways you can install _Black_. If you're looking to integrate _Black_
with different editors and environments, check the
[Integrations](../integrations/index.md) section instead.

## Install from PyPI

To install the latest release of _Black_ from [PyPI](https://pypi.org/project/black/)
(Requires Python {{ SUPPORTED_PYTHON_VERSION }}), use:

`pip install black`

_Black_ also publishes a number of extras. These are optional modules, designed to add
functionality to the core _Black_ package.

| extra    | Description                                                   | command                       |
| -------- | ------------------------------------------------------------- | ----------------------------- |
| jupyter  | Allows formatting of Jupyter notebooks                        | `pip install black[jupyter]`  |
| d        | Run _Black_ as a [server](./black_as_a_server.md)             | `pip install black[d]`        |
| colorama | Enables colored diffs in Windows environments                 | `pip install black[colorama]` |
| uvloop   | Speeds up _Black_ when concurrently formatting multiple files | `pip install black[uvloop]`   |

A _Black_ release currently offers three types of artifacts via PyPI, as outlined in the
[Release Process](../contributing/release_process.md):

1. The source distribution of the release
2. Generic Python wheel, meant for use on any Python supported platform
3. Platform and Python version specific wheels that offer significantly improved
   performance, compiled using [mypyc](https://mypyc.readthedocs.io/)

By default, `pip` will prefer a compatible wheel and revert to the source distribution
if no such wheels are found, as outlined in
[Python documentation](https://packaging.python.org/en/latest/tutorials/installing-packages/#source-distributions-vs-wheels).

## Install from GitHub

To install the latest commit of _Black_ from the GitHub 'main' branch, use:

`pip install git+https://github.com/psf/black`

## Get native binaries from GitHub

[GitHub Releases](https://github.com/psf/black/releases) for _Black_ contain
self-contained, native binaries for multiple platforms (built using PyInstaller). This
allows you to download the executable for your platform and run _Black_ without a Python
runtime installed.

## Black Docker images

Official _Black_ Docker images are available on
[Docker Hub](https://hub.docker.com/r/pyfound/black). For more information on its usage,
check the [Black Docker image](./black_docker_image) section.
