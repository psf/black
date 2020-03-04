FROM python:3

RUN pip install git+https://github.com/psf/black.git
RUN git config --global user.email "nobody@example.com"
RUN git config --global user.name "BlackBot"

COPY entrypoint.sh /src/entrypoint.sh
ENTRYPOINT ["/src/entrypoint.sh"]
