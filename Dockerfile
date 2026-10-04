FROM python:3.15-slim AS builder

ENV VIRTUAL_ENV=/opt/venv
ENV HATCH_BUILD_HOOKS_ENABLE=1
ENV PIP_NO_CACHE_DIR=1

# Install build tools to compile black + dependencies
RUN apt update && apt install -y build-essential git

WORKDIR /src
COPY . .
RUN python -m venv --without-pip $VIRTUAL_ENV

# virtualenv 20.39 uses pip 26.0 - use `ENV ...=P2D` once we bump virtualenv/hatch
RUN export PIP_UPLOADED_PRIOR_TO=$(date -u -d "2 days ago" +%Y-%m-%dT%H:%M:%SZ) \
    && pip install --upgrade pip \
    && pip install --group hatch \
    && hatch build -t wheel

ENV PIP_PYTHON=$VIRTUAL_ENV/bin/python
RUN pip install dist/*-cp* "black[colorama,d,uvloop]"

FROM python:3.15-slim

# copy only Python packages to limit the image size
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

CMD ["/opt/venv/bin/black"]
