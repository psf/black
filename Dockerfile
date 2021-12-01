FROM python:3-slim AS builder

RUN mkdir /src
COPY . /src/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    # Install build tools to compile dependencies that don't have prebuilt wheels
    && apt update && apt install -y git build-essential \
    && cd /src \
    && pip install --user --no-cache-dir .[colorama,d]

FROM python:3-slim

# copy only Python packages to limit the image size
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

CMD ["black"]
