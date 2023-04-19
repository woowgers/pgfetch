import asyncio
from hashlib import sha256
from pathlib import Path
import logging

import aiofiles

from project.giteaapi import FileContent, GiteaRepositoryApi


class RepositoryFileFetcher:
    def __init__(self, host: str, org: str, repo: str, branch: str):
        self.api = GiteaRepositoryApi(host=host, org=org, repo=repo, branch=branch)

    async def _write_file(
        self,
        local_filepath: Path,
        remote_filepath: Path,
        content: FileContent,
        cksum_file: Path,
        cksum_file_lock: asyncio.Lock,
    ):
        parent_dir = local_filepath.parent
        parent_dir.mkdir(parents=True, exist_ok=True)

        cksum = sha256(content.bytes).hexdigest()
        async with aiofiles.open(local_filepath, "wb") as f_content:
            await f_content.write(content.bytes)
        async with cksum_file_lock, aiofiles.open(cksum_file, "a") as f_cksum:
            await f_cksum.write(f"{remote_filepath}\t{cksum}\n")

    async def save_file_content(
        self,
        filepath: Path,
        root_dir: Path,
        cksum_file: Path,
        cksum_file_lock: asyncio.Lock,
        n_tasks_sem: asyncio.Semaphore,
    ):
        async with n_tasks_sem:
            logging.info(f"saving {filepath}...")
            local_filepath = root_dir / filepath
            content = await self.api.get_file_content(filepath)
            await self._write_file(local_filepath, filepath, content, cksum_file, cksum_file_lock)
            logging.info(f"{filepath} saved")

    async def save_contents(self, root_dir: str | Path, cksum_file: str | Path, n_tasks_max: int = 100):
        root_dir = Path(root_dir)
        cksum_file = Path(cksum_file)
        cksum_file.unlink(missing_ok=True)

        tree = await self.api.get_branch_tree()

        n_tasks_sem = asyncio.Semaphore(n_tasks_max)
        cksum_file_lock = asyncio.Lock()
        tasks = (
            self.save_file_content(entry.path, root_dir, cksum_file, cksum_file_lock, n_tasks_sem)
            for entry in tree.files
        )
        await asyncio.gather(*tasks)
