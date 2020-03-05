FROM python:3-slim

RUN apt-get update && apt-get install -y git

RUN git config --global user.email "nobody@example.com"
RUN git config --global user.name "BlackBot"

COPY entrypoint.sh /src/entrypoint.sh
ENTRYPOINT ["/src/entrypoint.sh"]
