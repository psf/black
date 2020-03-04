FROM python:3.8.2-slim

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install git apt-utils -y

RUN git config --global user.email "black@psf.github.com"
RUN git config --global user.name "Gallery/Black"

COPY gallery.py /
ENTRYPOINT ["python", "/gallery.py"]
