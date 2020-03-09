# Gallery

Gallery is a script that automates process of applying different black versions to a
selected PyPI package and seeing the results between black versions.

## Build

```console
$ [sudo] docker build -t black_gallery .
```

## Run

```console
$ sudo docker run -it -v /host/output:/output -v /host/input:/input black_gallery:latest [args]
```

```
usage: gallery.py [-h] -p PYPI_PACKAGE -b BLACK_REPO [-v VERSION] [-i INPUT] [-o OUTPUT] [versions ...]

Black Gallery is a script that automates process of applying different black versions to a selected PyPI package and seeing the results between versions.

positional arguments:
  versions

optional arguments:
  -h, --help            show this help message and exit
  -p PYPI_PACKAGE, --pypi-package PYPI_PACKAGE
                        PyPI package to download.
  -b BLACK_REPO, --black-repo BLACK_REPO
                        Black's git repository.
  -v VERSION, --version VERSION
                        Version for PyPI given pypi package.
  -i INPUT, --input INPUT
                        Input directory to read configurations.
  -o OUTPUT, --output OUTPUT
                        Output directory to download and put result artifacts.
```
