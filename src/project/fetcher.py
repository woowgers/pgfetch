import asyncio
import logging
from pathlib import Path

import aiofiles

from project.api.base import BaseRepositoryBranchApi
from project.models import GitTree


class RepositoryBranchFetcher:
    def __init__(self, api: BaseRepositoryBranchApi):
        self.api = api

    async def fetch_files(self, root_dir: Path, n_tasks_max: int = 100) -> None:
        if n_tasks_max <= 0:
            raise ValueError(f"`n_tasks_max` must not be negative")

        tree = await self._get_branch_tree()

        async with asyncio.TaskGroup() as g:
            for file_entry in tree.files:
                g.create_task(
                    self._fetch_file(
                        root_dir,
                        file_entry.path,
                        await self._create_semaphore(n_tasks_max),
                    )
                )

    async def _create_semaphore(self, n_tasks_max):
        return asyncio.Semaphore(n_tasks_max)

    async def _get_branch_tree(self) -> GitTree:
        return await self.api.get_branch_tree()

    async def _write_file_content(self, *, local_filepath: Path, content: str) -> None:
        local_filepath.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(local_filepath, "w") as f:
            await f.write(content)

    async def _fetch_file(
        self, root_dir: Path, filepath: Path, n_tasks_sem: asyncio.Semaphore
    ) -> None:
        async with n_tasks_sem:
            logging.info(f"saving {filepath}...")

            local_filepath = root_dir / filepath

            await self._write_file_content(
                local_filepath=local_filepath,
                content=await self._get_file_content(filepath),
            )

            logging.info(f"{filepath} saved")

    async def _get_file_content(self, filepath: Path) -> str:
        return await self.api.get_file_content(filepath)
