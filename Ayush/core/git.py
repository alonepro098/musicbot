import asyncio
import shlex
from typing import Tuple

try:
    from git import Repo
    from git.exc import GitCommandError, InvalidGitRepositoryError
except ImportError:
    Repo = None
    GitCommandError = Exception
    InvalidGitRepositoryError = Exception

import config

from ..logging import LOGGER


def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(install_requirements())


def git():
    if Repo is None:
        LOGGER(__name__).warning("GitPython package not installed. Skipping git updates.")
        return

    if not config.UPSTREAM_REPO:
        return

    REPO_LINK = config.UPSTREAM_REPO
    if config.GIT_TOKEN:
        try:
            GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
            TEMP_REPO = REPO_LINK.split("https://")[1]
            UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
        except Exception:
            UPSTREAM_REPO = config.UPSTREAM_REPO
    else:
        UPSTREAM_REPO = config.UPSTREAM_REPO

    try:
        try:
            repo = Repo()
            LOGGER(__name__).info("Git Client Found")
        except (GitCommandError, InvalidGitRepositoryError):
            LOGGER(__name__).info("Running standalone deployment, skipping git overwrite.")
            return
            
        if "origin" in repo.remotes:
            origin = repo.remote("origin")
        else:
            origin = repo.create_remote("origin", UPSTREAM_REPO)
            
        try:
            origin.fetch(config.UPSTREAM_BRANCH)
            LOGGER(__name__).info("Fetched updates from upstream repository.")
        except Exception:
            pass
    except Exception as e:
        LOGGER(__name__).warning(f"Git auto-update skipped: {e}")

