FROM python:3.12-slim AS builder

RUN mkdir /src
COPY . /src/
ENV VIRTUAL_ENV=/opt/venv
ENV HATCH_BUILD_HOOKS_ENABLE=1
# Install build tools to compile black + dependencies
RUN apt update && apt install -y build-essential git python3-dev
RUN python -m venv $VIRTUAL_ENV
RUN python -m pip install --no-cache-dir hatch hatch-fancy-pypi-readme hatch-vcs
RUN . /opt/venv/bin/activate && pip install --no-cache-dir --upgrade pip setuptools \
    && cd /src && hatch build -t wheel \
    && pip install --no-cache-dir dist/*-cp*[colorama,d,uvloop]

FROM python:3.12-slim

# copy only Python packages to limit the image size
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

CMD ["/opt/venv/bin/black"]
