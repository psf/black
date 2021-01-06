#!/bin/sh
set -e

# If no arguments are given use current working directory
black_args=(".")
if [ "$#" -eq 0 ] && [ "${INPUT_BLACK_ARGS}" != "" ]; then
  black_args+=(${INPUT_BLACK_ARGS})
elif [ "$#" -ne 0 ] && [ "${INPUT_BLACK_ARGS}" != "" ]; then
  black_args+=($* ${INPUT_BLACK_ARGS})
elif [ "$#" -ne 0 ] && [ "${INPUT_BLACK_ARGS}" == "" ]; then
  black_args+=($*)
else
  # Default (if no args provided).
  black_args+=("--check" "--diff")
fi

sh -c "black . ${black_args[@]}" || black_exit_val="$?"

# Throw error if an error occurred and fail_on_error is true
if [[ "${INPUT_FAIL_ON_ERROR,,}" = 'true' && "${black_error}" = 'true' ]]; then
  exit 1
fi