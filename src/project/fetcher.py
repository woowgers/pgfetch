import asyncio
import logging
from pathlib import Path
from typing import Self

import aiofiles
import aiohttp

from project.giteaapi import GiteaRepositoryBranchApi


class GiteaRepositoryBranchFetcher:
    def __init__(self, host: str, org: str, repo: str, branch: str):
        self.api = GiteaRepositoryBranchApi(host, org, repo, branch)

    async def __aenter__(self) -> Self:
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *_) -> None:
        await self.session.close()

    async def _write_file_content(self, local_filepath: Path, content: str) -> None:
        local_filepath.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(local_filepath, "w") as f:
            await f.write(content)

    async def _fetch_file(self, root_dir: Path, filepath: Path, n_tasks_sem: asyncio.Semaphore) -> None:
        async with n_tasks_sem:
            logging.info(f"saving {filepath}...")
            local_filepath = root_dir / filepath
            content = await self.api.get_file_content(self.session, filepath)
            await self._write_file_content(local_filepath, content)
            logging.info(f"{filepath} saved")

    async def fetch_files(self, root_dir: Path, n_tasks_max: int = 100) -> None:
        if n_tasks_max <= 0:
            raise ValueError(f"`n_tasks_max` must not be negative")

        tree = await self.api.get_branch_tree(self.session)
        n_tasks_sem = asyncio.Semaphore(n_tasks_max)
        async with asyncio.TaskGroup() as g:
            for file_entry in tree.files:
                g.create_task(self._fetch_file(root_dir, file_entry.path, n_tasks_sem))
