FROM python:3.15-slim AS builder

ENV VIRTUAL_ENV=/opt/venv
ENV HATCH_BUILD_HOOKS_ENABLE=1
ENV PIP_NO_CACHE_DIR=1

# Install build tools to compile black + dependencies
RUN apt update && apt install -y build-essential git

WORKDIR /src
COPY . .
RUN python -m venv --without-pip $VIRTUAL_ENV

RUN export PIP_UPLOADED_PRIOR_TO=P2D \
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
