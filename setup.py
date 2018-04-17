# Copyright (C) 2018 Łukasz Langa
import ast
import re
from setuptools import setup
import sys

assert sys.version_info >= (3, 6, 0), "black requires Python 3.6+"
from pathlib import Path  # noqa E402

CURRENT_DIR = Path(__file__).parent


def get_long_description():
    readme_md = CURRENT_DIR / "README.md"
    with open(readme_md, encoding="utf8") as ld_file:
        return ld_file.read()


def get_version():
    black_py = CURRENT_DIR / "black.py"
    _version_re = re.compile(r"__version__\s+=\s+(?P<version>.*)")
    with open(black_py, "r", encoding="utf8") as f:
        version = _version_re.search(f.read()).group("version")
    return str(ast.literal_eval(version))


setup(
    name="black",
    version=get_version(),
    description="The uncompromising code formatter.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    keywords="automation formatter yapf autopep8 pyfmt gofmt rustfmt",
    author="Łukasz Langa",
    author_email="lukasz@langa.pl",
    url="https://github.com/ambv/black",
    license="MIT",
    py_modules=["black"],
    packages=["blib2to3", "blib2to3.pgen2"],
    package_data={"blib2to3": ["*.txt"]},
    python_requires=">=3.6",
    zip_safe=False,
    install_requires=["click", "attrs>=17.4.0", "appdirs"],
    test_suite="tests.test_black",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    entry_points={"console_scripts": ["black=black:main"]},
)
