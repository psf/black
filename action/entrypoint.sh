#!/bin/bash
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

sh -c "black . ${black_args[*]}"
