```shell
docker build -t black-gallery .
docker run -it -v "$(pwd)/main.py:/main.py:ro" -v "$(pwd)/output/:/output/" black-gallery -p Django -v 3.0 19.10b0
```
