import asyncio
from asyncio.tasks import Task
import logging
from pathlib import Path

import aiofiles

from project.giteaapi import GiteaRepositoryBranchApi
from project.types import GitTree


class RepositoryFileFetcher:
    def __init__(self, host: str, org: str, repo: str, branch: str):
        self.api = GiteaRepositoryBranchApi(host=host, org=org, repo=repo, branch=branch)

    async def _write_file_content(self, local_filepath: Path, content: bytes) -> None:
        local_filepath.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(local_filepath, "wb") as f:
            await f.write(content)

    async def _fetch_file(self, root_dir: str | Path, filepath: Path, n_tasks_sem: asyncio.Semaphore) -> None:
        async with n_tasks_sem:
            logging.info(f"saving {filepath}...")
            local_filepath = root_dir / filepath
            content = await self.api.get_file_content(filepath)
            await self._write_file_content(local_filepath, content.bytes)
            logging.info(f"{filepath} saved")

    def _construct_tasks(self, tree: GitTree, root_dir: Path, n_tasks_sem: asyncio.Semaphore) -> tuple[Task, ...]:
        return tuple(asyncio.create_task(self._fetch_file(entry.path, root_dir, n_tasks_sem)) for entry in tree.files)

    async def fetch_files(self, root_dir: str, n_tasks_max: int = 100) -> None:
        if n_tasks_max <= 0:
            raise ValueError(f"`n_tasks_max` must not be negative")

        tree = await self.api.get_branch_tree()
        n_tasks_sem = asyncio.Semaphore(n_tasks_max)
        async with asyncio.TaskGroup() as g:
            g.create_task(self._fetch_file(root_dir, entry.path, n_tasks_sem) for entry in tree.files)
