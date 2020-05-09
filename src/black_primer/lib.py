#!/usr/bin/env python3

import asyncio
import json
import logging
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError
from sys import version_info
from typing import Dict, Optional, Sequence, Tuple, Union
from urllib.parse import urlparse

import click


LOG = logging.getLogger(__name__)


async def _gen_check_output(
    cmd: Sequence[str],
    timeout: Union[int, float] = 30,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[Path] = None,
) -> Tuple[bytes, bytes]:
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=env,
        cwd=cwd,
    )
    try:
        (stdout, stderr) = await asyncio.wait_for(process.communicate(), timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise

    if process.returncode != 0:
        cmd_str = " ".join(cmd)
        raise CalledProcessError(
            process.returncode, cmd_str, output=stdout, stderr=stderr
        )

    return (stdout, stderr)


async def analyze_results(project_count: int, results: Dict) -> int:
    failed_pct = round(((results["failed"] / project_count) * 100), 2)
    success_pct = round(((results["success"] / project_count) * 100), 2)

    click.secho(f"-- primer results 📊 --\n", bold=True)
    click.secho(
        f"{results['success']} / {project_count} succeeded ({success_pct}%) ✅",
        bold=True,
        fg="green",
    )
    click.secho(
        f"{results['failed']} / {project_count} FAILED ({failed_pct}%) 💩",
        bold=bool(results["failed"]),
        fg="red",
    )
    click.echo(f" - {results['disabled']} projects Disabled by config")
    click.echo(f" - {results['wrong_py_ver']} projects skipped due to Python Version ")
    click.echo(f" - {results['skipped_long_checkout']} skipped due to long checkout")

    if results["projects"]:
        click.secho(f"\nFailed Projects:\n", bold=True)

    for project_name, project_cpe in results["projects"].items():
        print(f"## {project_name}:")
        print(f" - Returned {project_cpe.returncode}")
        if project_cpe.stderr:
            print(f" - stderr:\n{project_cpe.stderr.decode('utf8')}")
        if project_cpe.stdout:
            print(f" - stdout:\n{project_cpe.stdout.decode('utf8')}")
        print("")

    return results["failed"]


async def black_run(repo_path: Path, project_config: Dict, results: Dict) -> None:
    """Run black and record failures"""
    cmd = [which("black")]
    if project_config["cli_arguments"]:
        cmd.extend(project_config["cli_arguments"])
    cmd.extend(["--check", "--diff", "."])

    try:
        _stdout, _stderr = await _gen_check_output(cmd, cwd=repo_path)
    except asyncio.TimeoutError:
        results["failed"] += 1
        LOG.error(f"Running black for {repo_path} timedout ({cmd})")
    except CalledProcessError as cpe:
        # TODO: This might need to be tuned and made smarter for higher signal
        if not project_config["expect_formatting_changes"] and cpe.returncode == 1:
            results["failed"] += 1
            results["projects"][repo_path.name] = cpe
            return

    results["success"] += 1


async def git_checkout_or_rebase(
    work_path: Path, project_config: Dict, rebase: bool = False
) -> Optional[Path]:
    """git Clone project or rebase"""
    git_bin = which("git")
    repo_url_parts = urlparse(project_config["git_clone_url"])
    path_parts = repo_url_parts.path[1:].split("/", maxsplit=1)

    repo_path = work_path / path_parts[1].replace(".git", "")
    cmd = [git_bin, "clone", project_config["git_clone_url"]]
    cwd = work_path
    if repo_path.exists():
        cmd = [git_bin, "pull", "--rebase"]
        cwd = repo_path

    try:
        _stdout, _stderr = await _gen_check_output(cmd, cwd=cwd)
    except (asyncio.TimeoutError, CalledProcessError) as e:
        LOG.error(f"Unable to git clone / pull {project_config['git_clone_url']}: {e}")
        return None

    return repo_path


async def load_projects_queue(config_path: Path) -> Tuple[Dict, asyncio.Queue]:
    """Load project config and fill queue with all the project names"""
    with config_path.open("r") as cfp:
        config = json.load(cfp)

    # TODO: Offer more options here
    # e.g. Run on X random packages or specific sub list etc.
    project_names = sorted(config["projects"].keys())
    queue: asyncio.Queue = asyncio.Queue(maxsize=len(project_names))
    for project in project_names:
        await queue.put(project)

    return config, queue


async def project_runner(
    idx: int,
    config: Dict,
    queue: asyncio.Queue,
    work_path: Path,
    results: Dict,
    long_checkouts: bool = False,
    rebase: bool = False,
) -> None:
    """Checkout project and run black on it + record result"""
    py_version = f"{version_info[0]}.{version_info[1]}"
    while True:
        try:
            project_name = queue.get_nowait()
        except asyncio.QueueEmpty:
            LOG.debug(f"project_runner {idx} exiting")
            return

        project_config = config["projects"][project_name]

        # Check if disabled by config
        if "disabled" in project_config and project_config["disabled"]:
            results["disabled"] += 1
            LOG.info(f"Skipping {project_name} as it's disabled via config")
            continue

        # Check if we should run on this version of Python
        if (
            "all" not in project_config["py_versions"]
            and py_version not in project_config["py_versions"]
        ):
            results["wrong_py_ver"] += 1
            LOG.debug(f"Skipping {project_name} as it's not enabled for {py_version}")
            continue

        # Check if we're doing big projects / long checkouts
        if not long_checkouts and project_config["long_checkout"]:
            results["skipped_long_checkout"] += 1
            LOG.debug(f"Skipping {project_name} as it's configured as a long checkout")
            continue

        repo_path = await git_checkout_or_rebase(work_path, project_config, rebase)
        await black_run(repo_path, project_config, results)


async def process_queue(
    config: str,
    work_path: Path,
    workers: int,
    keep: bool = False,
    long_checkouts: bool = False,
    rebase: bool = False,
) -> int:
    """
    Process the queue with X workers and evaluate results
    - Success is guaged via the config "expect_formatting_changes"

    Integer return equals the number of failed projects
    """
    results: Dict[str, Dict] = {}
    results["disabled"] = 0
    results["failed"] = 0
    results["skipped_long_checkout"] = 0
    results["success"] = 0
    results["wrong_py_ver"] = 0
    results["projects"]: Dict[str, CalledProcessError] = {}

    config, queue = await load_projects_queue(Path(config))
    project_count = queue.qsize()
    LOG.info(f"{project_count} projects to run black over")
    if not project_count:
        return -1

    LOG.debug(f"Using {workers} parallel workers to run black")
    # Wait until we finish running all the projects before analyzing
    await asyncio.gather(
        *[
            project_runner(i, config, queue, work_path, results, long_checkouts, rebase)
            for i in range(workers)
        ]
    )

    LOG.info("Analyzing results")
    return await analyze_results(project_count, results)
