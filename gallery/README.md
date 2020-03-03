# Usage

```
docker build -t black_gallery .

docker run -ti -v /tmp/somedir/:/output black_gallery \
  -p Django \
  -v 3.0.3 \
  19.3b0 19.10b0 master
```

Examples:

- https://foss.heptapod.net/pypy/pypy/repository/branch/default/archive.tar.bz2


Tests:

```
docker run -it -v /tmp/output:/output black_gallery

-p Twisted 19.10b0:pyproject-19.10b0.toml master:pyproject-master.toml
-p Django -v 3.0.3 19.3b0 19.10b0 master
-p cpython -v v3.9.0a4
```
