FROM python:3

RUN pip install git+https://github.com/psf/black.git
RUN git config --local user.email "nobody@example.com"
RUN git config --local user.name "BlackBot"

COPY entrypoint.sh /src/entrypoint.sh
ENTRYPOINT ["/src/entrypoint.sh"]
