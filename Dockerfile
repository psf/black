FROM python:3-slim AS builder

RUN mkdir /src
COPY . /src/
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
RUN . /opt/venv/bin/activate && pip install --no-cache-dir --upgrade pip setuptools wheel \
    # Install build tools to compile dependencies that don't have prebuilt wheels
    && apt update && apt install -y git build-essential \
    && cd /src \
    && pip install --no-cache-dir .[colorama,d]

FROM python:3-slim

# copy only Python packages to limit the image size
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

CMD ["/opt/venv/bin/black"]
