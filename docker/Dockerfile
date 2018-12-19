FROM alpine:3.6

RUN apk add --no-cache --update python3 \
      && apk add --no-cache --virtual .build-deps py-pip \
      && pip3 --no-cache-dir install black \
      && apk del --no-cache --purge .build-deps \
      && rm -rf /usr/lib/python2.* \
      && rm -rf /var/cache/* \
      && rm -rf /root/.cache/* \
      && find /usr/lib/python* -depth \( -name '*.pyo' -o -name '*.pyc' -o -name 'test' -o -name 'tests' \) -exec rm -rf '{}' + ;

ENTRYPOINT ["/usr/bin/black" ]
CMD ["--help"]
