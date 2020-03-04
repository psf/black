# Usage

This tool allows you to view the format changes that Black would make on a given Python package given any permutation of Black config and version.

## Setup

Build the image:

```
docker build -t black_gallery .. -f Dockerfile

## Usage

You'll want to bind-mount a volume on your host, e.g. `-v /tmp/output/:/output`, where this tool will place its output.

Then, run with a command such as the following:

```

docker run -ti -v /tmp/output/:/output black_gallery \
 -p Django \
 -v 3.0.3 \
 19.3b0 19.10b0 master

```

where:
- `-p` is the package to test (`cpython` and `mypy` values are specially treated)
- `-v` is the package version

Any further arguments are interpreted as versions of Black, e.g. `master`.

Running a command like the one above will mount your local `/tmp/output/` directory, pull remote sources, format them with Black, and commit the results to a branch corresponding to the requested Black version.

To run Black with a custom config, you can place a Black config file in `/tmp/output` and specify it with `:configFileName.toml` appended to the Black version, as in `master:configfile.toml`.

## Examples

# Django 3.0.3 with various Black version/config permutations
```

docker run -ti -v /tmp/output/:/output black_gallery \
 -p Django \
 -v 3.0.3 \
 19.3b0:someconfig.toml 19.10b0:someotherconfig.toml master:pyproject.toml

```

### latest Twisted with various Black version/config permutations

```

docker run -it -v /tmp/output:/output black_gallery \
 -p Twisted \
 19.10b0:pyproject-19.10b0.toml master:pyproject-master.toml

```

### cpython version 3.9.0a4 with Black master

```

docker run -it -v /tmp/output:/output black_gallery \
 -p cpython -v v3.9.0a4

```

```
