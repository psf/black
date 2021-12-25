import shutil
from pathlib import Path
from typing import Union

import nox

SUPPORTED_PYTHONS = ["3.6", "3.7", "3.8", "3.9", "3.10", "pypy3"]
THIS_DIR = Path(__file__).parent
TESTS_DIR = THIS_DIR / "tests"
SCRIPTS_DIR = THIS_DIR / "scripts"

# ============ #
# Utilities
# ============ #


def get_flag(session: nox.Session, flag: str) -> bool:
    if flag in session.posargs:
        index = session.posargs.index(flag)
        del session.posargs[index]
        return True

    return False


def wipe(session: nox.Session, path: Union[str, Path]) -> None:
    if isinstance(path, str):
        path = Path.cwd() / path
    if not path.exists():
        return

    normalized = path.relative_to(Path.cwd())
    if path.is_file():
        session.log(f"Deleting '{normalized}' file")
        path.unlink()
    elif path.is_dir():
        session.log(f"Deleting '{normalized}' directory")
        shutil.rmtree(path)


# ============ #
# Sessions
# ============ #


@nox.session()
def lint(session: nox.Session) -> None:
    session.install("pre-commit>=2.9.2")
    session.run("pre-commit", "run", "--all-files", "--show-diff-on-failure")


@nox.session(python=SUPPORTED_PYTHONS)
def tests(session: nox.Session) -> None:
    coverage = not get_flag(session, "--no-cov")
    parallelize = not get_flag(session, "--no-xdist")

    session.install("-r", str(TESTS_DIR / "requirements.txt"))
    session.install(".[d]")
    base = ["pytest", str(TESTS_DIR), "-Wall", "--strict-config", "--strict-markers"]
    if coverage:
        session.run("coverage", "erase")
        base.extend(("--cov", "--cov-append"))
    if parallelize:
        base.extend(("--numprocesses", "auto"))

    session.run("python", "-m", "pip", "uninstall", "ipython", "-y")
    session.run(*base, "--run-optional=no_jupyter", *session.posargs)
    session.install(".[jupyter]")
    session.run(*base, "--run-optional=jupyter", "-m", "jupyter", *session.posargs)
    if coverage:
        session.run("coverage", "report")


@nox.session()
def docs(session: nox.Session) -> None:
    session.install("-e", ".[d]")
    session.cd("docs")
    wipe(session, "_build")
    session.install("-r", "requirements.txt")
    session.run("sphinx-build", ".", "_build", "-E", "-W", "-a", "--keep-going")


@nox.session(name="docs-live")
def docs_live(session: nox.Session) -> None:
    session.install("-e", ".[d]")
    session.cd("docs")
    wipe(session, "_build")
    session.install("-r", "requirements.txt", "sphinx-autobuild")
    session.run(
        "sphinx-autobuild", ".", "_build", "--ignore", "**/pypi.svg", *session.posargs
    )


@nox.session()
def fuzz(session: nox.Session) -> None:
    session.install("-r", str(TESTS_DIR / "requirements.txt"), "hypothesmith")
    session.install(".")
    session.run("coverage", "erase")
    session.run("coverage", "run", str(SCRIPTS_DIR / "fuzz.py"))
    session.run("coverage", "report")
