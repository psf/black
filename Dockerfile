FROM python:3-slim

RUN pip install --upgrade pip setuptools wheel
RUN apt update && apt install -y git
RUN mkdir /src
COPY . /src/
RUN cd /src && pip install --no-cache-dir .
RUN rm -rf /src && apt remove -y git && apt autoremove -y

CMD ["black"]
