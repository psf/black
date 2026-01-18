FROM python:3.13-slim AS builder

RUN mkdir /src
COPY . /src/
ENV VIRTUAL_ENV=/opt/venv
ENV HATCH_BUILD_HOOKS_ENABLE=1
# Install build tools to compile black + dependencies
RUN apt update && apt install -y build-essential git python3-dev

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV
RUN cd /src \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --group build \
    && hatch build -t wheel \
    && pip install --no-cache-dir dist/*-cp* \
    && pip install black[colorama,d,uvloop]

FROM python:3.13-slim

# copy only Python packages to limit the image size
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

CMD ["/opt/venv/bin/black"]
