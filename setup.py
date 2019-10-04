# Copyright (C) 2018 Łukasz Langa
from setuptools import setup
import sys

assert sys.version_info >= (3, 6, 0), "black requires Python 3.6+"

if __name__ == "__main__":
    setup(use_scm_version=True)
