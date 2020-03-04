# Usage

```
docker build -t black_gallery .

docker run -ti -v /tmp/output/:/output black_gallery \
  -p Django \
  -v 3.0.3 \
  19.3b0 19.10b0 master
```

where:
- `-p` is the package to test (`cpython` and `mypy` values are specially treated)
- `-v` is the package version

Further arguments are interpreted as versions of Black
You can place a Black config file in `/tmp/output` and specify it with `:configFileName.toml` appended to the Black version, like so:

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
