import asyncio
from collections.abc import Sequence
import logging
from hashlib import sha256
from pathlib import Path
from typing import Coroutine

import aiofiles

from project.giteaapi import GiteaRepositoryApi
from project.types import GitEntry, GitTree


class RepositoryFileFetcher:
    def __init__(self, host: str, org: str, repo: str, branch: str):
        self.api = GiteaRepositoryApi(host=host, org=org, repo=repo, branch=branch)

    async def _write_file_cksum(
        self, remote_filepath: Path, content: bytes, cksum_file: Path, cksum_file_lock: asyncio.Lock
    ):
        cksum = sha256(content).hexdigest()
        async with cksum_file_lock, aiofiles.open(cksum_file, "a") as f_cksum:
            await f_cksum.write(f"{remote_filepath}\t{cksum}\n")

    async def _write_file_content(self, local_filepath: Path, content_bytes: bytes):
        local_filepath.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(local_filepath, "wb") as f_content:
            await f_content.write(content_bytes)

    async def save_file_to_local_dir(
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
            await self._write_file_cksum(filepath, content.bytes, cksum_file, cksum_file_lock)
            await self._write_file_content(local_filepath, content.bytes)
            logging.info(f"{filepath} saved")

    def _construct_tasks(self, tree: GitTree, root_dir: Path, cksum_file: Path, cksum_file_lock: asyncio.Lock, n_tasks_sem: asyncio.Semaphore) -> tuple[Coroutine]:
        return tuple(
            self.save_file_to_local_dir(entry.path, root_dir, cksum_file, cksum_file_lock, n_tasks_sem)
            for entry in tree.files
        )

    async def save_contents(self, root_dir: str | Path, cksum_file: str | Path, n_tasks_max: int = 100):
        root_dir = Path(root_dir)
        cksum_file = Path(cksum_file)
        cksum_file.unlink(missing_ok=True)

        tree = await self.api.get_branch_tree()

        n_tasks_sem = asyncio.Semaphore(n_tasks_max)
        cksum_file_lock = asyncio.Lock()
        await asyncio.gather(*self._construct_tasks(tree, root_dir, cksum_file, cksum_file_lock, n_tasks_sem))
