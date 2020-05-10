from enum import Enum
from multiprocessing import freeze_support
from pathlib import Path

import click
import toml
from black import __version__
from black.defaults import (DEFAULT_EXCLUDES, DEFAULT_INCLUDES,
                            DEFAULT_LINE_LENGTH)
from black.formatter import Mode, TargetVersion
from black.reporting import Report
from black.source import WriteBack, get_sources
from black.tasks import reformat_many, reformat_one
from black.types import *
from black.util import find_project_root, out, path_empty


def target_version_option_callback(
    c: click.Context, p: Union[click.Option, click.Parameter], v: Tuple[str, ...]
) -> List[TargetVersion]:
    """Compute the target versions from a --target-version flag.

    This is its own function because mypy couldn't infer the type correctly
    when it was a lambda, causing mypyc trouble.
    """
    return [TargetVersion[val.upper()] for val in v]


def read_pyproject_toml(
    ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[str]:
    """Inject Black configuration from "pyproject.toml" into defaults in `ctx`.

    Returns the path to a successfully found and read configuration file, None
    otherwise.
    """

    def find_pyproject_toml(path_search_start: str) -> Optional[str]:
        """Find the absolute filepath to a pyproject.toml if it exists"""
        path_project_root = find_project_root(path_search_start)
        path_pyproject_toml = path_project_root / "pyproject.toml"
        return str(path_pyproject_toml) if path_pyproject_toml.is_file() else None

    def parse_pyproject_toml(path_config: str) -> Dict[str, Any]:
        """Parse a pyproject toml file, pulling out relevant parts for Black

        If parsing fails, will raise a toml.TomlDecodeError
        """
        pyproject_toml = toml.load(path_config)
        config = pyproject_toml.get("tool", {}).get("black", {})
        return {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}

    if not value:
        value = find_pyproject_toml(ctx.params.get("src", ()))
        if value is None:
            return None

    try:
        config = parse_pyproject_toml(value)
    except (toml.TomlDecodeError, OSError) as e:
        raise click.FileError(
            filename=value, hint=f"Error reading configuration file: {e}"
        )

    if not config:
        return None

    target_version = config.get("target_version")
    if target_version is not None and not isinstance(target_version, list):
        raise click.BadOptionUsage(
            "target-version", f"Config key target-version must be a list"
        )

    default_map: Dict[str, Any] = {}
    if ctx.default_map:
        default_map.update(ctx.default_map)
    default_map.update(config)

    ctx.default_map = default_map
    return value


# ---- Command Line Interface ----


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-c", "--code", type=str, help="Format the code passed in as a string.")
@click.option(
    "-l",
    "--line-length",
    type=int,
    default=DEFAULT_LINE_LENGTH,
    help="How many characters per line to allow.",
    show_default=True,
)
@click.option(
    "-t",
    "--target-version",
    type=click.Choice([v.name.lower() for v in TargetVersion]),
    callback=target_version_option_callback,
    multiple=True,
    help=(
        "Python versions that should be supported by Black's output. [default: per-file"
        " auto-detection]"
    ),
)
@click.option(
    "--pyi",
    is_flag=True,
    help=(
        "Format all input files like typing stubs regardless of file extension (useful"
        " when piping source on standard input)."
    ),
)
@click.option(
    "-S",
    "--skip-string-normalization",
    is_flag=True,
    help="Don't normalize string quotes or prefixes.",
)
@click.option(
    "--check",
    is_flag=True,
    help=(
        "Don't write the files back, just return the status.  Return code 0 means"
        " nothing would change.  Return code 1 means some files would be reformatted."
        " Return code 123 means there was an internal error."
    ),
)
@click.option(
    "--diff",
    is_flag=True,
    help="Don't write the files back, just output a diff for each file on stdout.",
)
@click.option(
    "--color/--no-color",
    is_flag=True,
    help="Show colored diff. Only applies when `--diff` is given.",
)
@click.option(
    "--fast/--safe",
    is_flag=True,
    help="If --fast given, skip temporary sanity checks. [default: --safe]",
)
@click.option(
    "--include",
    type=str,
    default=DEFAULT_INCLUDES,
    help=(
        "A regular expression that matches files and directories that should be"
        " included on recursive searches.  An empty value means all files are included"
        " regardless of the name.  Use forward slashes for directories on all platforms"
        " (Windows, too).  Exclusions are calculated first, inclusions later."
    ),
    show_default=True,
)
@click.option(
    "--exclude",
    type=str,
    default=DEFAULT_EXCLUDES,
    help=(
        "A regular expression that matches files and directories that should be"
        " excluded on recursive searches.  An empty value means no paths are excluded."
        " Use forward slashes for directories on all platforms (Windows, too). "
        " Exclusions are calculated first, inclusions later."
    ),
    show_default=True,
)
@click.option(
    "--force-exclude",
    type=str,
    help=(
        "Like --exclude, but files and directories matching this regex will be "
        "excluded even when they are passed explicitly as arguments"
    ),
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help=(
        "Don't emit non-error messages to stderr. Errors are still emitted; silence"
        " those with 2>/dev/null."
    ),
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help=(
        "Also emit messages to stderr about files that were not changed or were ignored"
        " due to --exclude=."
    ),
)
@click.version_option(version=__version__)
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, allow_dash=True
    ),
    is_eager=True,
)
@click.option(
    "--config",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        allow_dash=False,
        path_type=str,
    ),
    is_eager=True,
    callback=read_pyproject_toml,
    help="Read configuration from PATH.",
)
@click.pass_context
def main(
    ctx: click.Context,
    code: Optional[str],
    line_length: int,
    target_version: List[TargetVersion],
    check: bool,
    diff: bool,
    color: bool,
    fast: bool,
    pyi: bool,
    skip_string_normalization: bool,
    quiet: bool,
    verbose: bool,
    include: str,
    exclude: str,
    force_exclude: Optional[str],
    src: Tuple[str, ...],
    config: Optional[str],
) -> None:
    """The uncompromising code formatter."""
    write_back = WriteBack.from_configuration(check=check, diff=diff, color=color)
    versions = (
        set(target_version) if target_version else set()
    )  # If empty, we autodetect later
    mode = Mode(
        target_versions=versions,
        line_length=line_length,
        is_pyi=pyi,
        string_normalization=not skip_string_normalization,
    )
    if config and verbose:
        out(f"Using configuration from {config}.", bold=False, fg="blue")

    if code is not None:
        print(format_str(code, mode=mode))
        ctx.exit(0)

    report = Report(check=check, diff=diff, quiet=quiet, verbose=verbose)

    sources = get_sources(
        ctx=ctx,
        src=src,
        quiet=quiet,
        verbose=verbose,
        include=include,
        exclude=exclude,
        force_exclude=force_exclude,
        report=report,
    )

    path_empty(
        sources,
        "No Python files are present to be formatted. Nothing to do 😴",
        quiet,
        verbose,
        ctx,
    )

    if len(sources) == 1:
        reformat_one(
            src=sources.pop(),
            fast=fast,
            write_back=write_back,
            mode=mode,
            report=report,
        )
    else:
        reformat_many(
            sources=sources, fast=fast, write_back=write_back, mode=mode, report=report
        )

    if verbose or not quiet:
        out("Oh no! 💥 💔 💥" if report.return_code else "All done! ✨ 🍰 ✨")
        click.secho(str(report), err=True)
    ctx.exit(report.return_code)


def patch_click() -> None:
    """Make Click not crash.

    On certain misconfigured environments, Python 3 selects the ASCII encoding as the
    default which restricts paths that it can access during the lifetime of the
    application.  Click refuses to work in this scenario by raising a RuntimeError.

    In case of Black the likelihood that non-ASCII characters are going to be used in
    file paths is minimal since it's Python source code.  Moreover, this crash was
    spurious on Python 3.7 thanks to PEP 538 and PEP 540.
    """
    try:
        from click import core
        from click import _unicodefun  # type: ignore
    except ModuleNotFoundError:
        return

    for module in (core, _unicodefun):
        if hasattr(module, "_verify_python3_env"):
            module._verify_python3_env = lambda: None


def patched_main() -> None:
    freeze_support()
    patch_click()
    main()


if __name__ == "__main__":
    patched_main()
