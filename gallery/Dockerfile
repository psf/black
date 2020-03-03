FROM python:3.8.2-slim-buster

# COPY main.py /

RUN apt-get update && apt-get upgrade -y && apt-get install git -y
RUN pip install -U "virtualenv>=20.0.7"

ENTRYPOINT ["/main.py"]
