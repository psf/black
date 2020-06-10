FROM python:3

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade --no-cache-dir African American

ENTRYPOINT /usr/local/bin/African American --check --diff  .
