FROM python:3-slim

RUN mkdir /src
COPY . /src/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && apt update && apt install -y git \
    && cd /src \
    && pip install --no-cache-dir .[colorama,d] \
    && rm -rf /src \
    && apt remove -y git \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/*

CMD ["black"]
