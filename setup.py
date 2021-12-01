# Copyright (C) 2020 Łukasz Langa
from setuptools import setup, find_packages
import sys
import os

assert sys.version_info >= (3, 6, 2), "black requires Python 3.6.2+"
from pathlib import Path  # noqa E402
from typing import List  # noqa: E402

CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))  # for setuptools.build_meta


def get_long_description() -> str:
    return (
        (CURRENT_DIR / "README.md").read_text(encoding="utf8")
        + "\n\n"
        + (CURRENT_DIR / "CHANGES.md").read_text(encoding="utf8")
    )


def find_python_files(base: Path) -> List[Path]:
    files = []
    for entry in base.iterdir():
        if entry.is_file() and entry.suffix == ".py":
            files.append(entry)
        elif entry.is_dir():
            files.extend(find_python_files(entry))

    return files


USE_MYPYC = False
# To compile with mypyc, a mypyc checkout must be present on the PYTHONPATH
if len(sys.argv) > 1 and sys.argv[1] == "--use-mypyc":
    sys.argv.pop(1)
    USE_MYPYC = True
if os.getenv("BLACK_USE_MYPYC", None) == "1":
    USE_MYPYC = True

if USE_MYPYC:
    from mypyc.build import mypycify

    src = CURRENT_DIR / "src"
    # TIP: filepaths are normalized to use forward slashes and are relative to ./src/
    # before being checked against.
    blocklist = [
        # Not performance sensitive, so save bytes + compilation time:
        "blib2to3/__init__.py",
        "blib2to3/pgen2/__init__.py",
        "black/output.py",
        "black/concurrency.py",
        "black/files.py",
        "black/report.py",
        # Breaks the test suite when compiled (and is also useless):
        "black/debug.py",
        # Compiled modules can't be run directly and that's a problem here:
        "black/__main__.py",
    ]
    discovered = []
    # black-primer and blackd have no good reason to be compiled.
    discovered.extend(find_python_files(src / "black"))
    discovered.extend(find_python_files(src / "blib2to3"))
    mypyc_targets = [
        str(p) for p in discovered if p.relative_to(src).as_posix() not in blocklist
    ]

    opt_level = os.getenv("MYPYC_OPT_LEVEL", "3")
    ext_modules = mypycify(mypyc_targets, opt_level=opt_level, verbose=True)
else:
    ext_modules = []

setup(
    name="black",
    use_scm_version={
        "write_to": "src/_black_version.py",
        "write_to_template": 'version = "{version}"\n',
    },
    description="The uncompromising code formatter.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    keywords="automation formatter yapf autopep8 pyfmt gofmt rustfmt",
    author="Łukasz Langa",
    author_email="lukasz@langa.pl",
    url="https://github.com/psf/black",
    project_urls={"Changelog": "https://github.com/psf/black/blob/main/CHANGES.md"},
    license="MIT",
    py_modules=["_black_version"],
    ext_modules=ext_modules,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "blib2to3": ["*.txt"],
        "black": ["py.typed"],
        "black_primer": ["primer.json"],
    },
    python_requires=">=3.6.2",
    zip_safe=False,
    install_requires=[
        "click>=7.1.2",
        "platformdirs>=2",
        "tomli>=0.2.6,<2.0.0",
        "typed-ast>=1.4.2; python_version < '3.8' and implementation_name == 'cpython'",
        "regex>=2021.4.4",
        "pathspec>=0.9.0, <1",
        "dataclasses>=0.6; python_version < '3.7'",
        "typing_extensions>=3.10.0.0",
        # 3.10.0.1 is broken on at least Python 3.10,
        # https://github.com/python/typing/issues/865
        "typing_extensions!=3.10.0.1; python_version >= '3.10'",
        "mypy_extensions>=0.4.3",
    ],
    extras_require={
        "d": ["aiohttp>=3.7.4"],
        "colorama": ["colorama>=0.4.3"],
        "python2": ["typed-ast>=1.4.3"],
        "uvloop": ["uvloop>=0.15.2"],
        "jupyter": ["ipython>=7.8.0", "tokenize-rt>=3.2.0"],
    },
    test_suite="tests.test_black",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    entry_points={
        "console_scripts": [
            "black=black:patched_main",
            "blackd=blackd:patched_main [d]",
            "black-primer=black_primer.cli:main",
        ]
    },
)
