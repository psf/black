# Gallery

Gallery is a script that automates the process of applying different _Black_ versions to
a selected PyPI package and seeing the results between _Black_ versions.

## Build

```console
$ docker build -t black_gallery .
```

## Run

```console
$ docker run -it -v /host/output:/output -v /host/input:/input black_gallery:latest [args]
```

```
usage: gallery.py [-h] (-p PYPI_PACKAGE | -t TOP_PACKAGES) [-b BLACK_REPO] [-v VERSION] [-w WORKERS] [-i INPUT] [-o OUTPUT]
                  [versions [versions ...]]

Black Gallery is a script that automates the process of applying different Black versions to a selected PyPI package and
seeing the results between versions.

positional arguments:
  versions

optional arguments:
  -h, --help            show this help message and exit
  -p PYPI_PACKAGE, --pypi-package PYPI_PACKAGE
                        PyPI package to download.
  -t TOP_PACKAGES, --top-packages TOP_PACKAGES
                        Top n PyPI packages to download.
  -b BLACK_REPO, --black-repo BLACK_REPO
                        Black's Git repository.
  -v VERSION, --version VERSION
                        Version for given PyPI package. Will be discarded if used with -t option.
  -w WORKERS, --workers WORKERS
                        Maximum number of threads to download with at the same time. Will be discarded if used with -p
                        option.
  -i INPUT, --input INPUT
                        Input directory to read configuration.
  -o OUTPUT, --output OUTPUT
                        Output directory to download and put result artifacts.
```
