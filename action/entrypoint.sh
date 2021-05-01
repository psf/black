#!/bin/bash -e

if [ -n $INPUT_BLACK_ARGS ]; then
  echo '::warning::Input `with.black_args` is deprecated. Use `with.options` and `with.src` instead.'
  black $INPUT_BLACK_ARGS
  exit $?

black $INPUT_OPTIONS $INPUT_SRC
