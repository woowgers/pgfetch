import asyncio
import aiofiles
from hashlib import sha256
from pathlib import Path
import logging

from giteaapi import GiteaRepositoryApi


class RepositoryFileFetcher:
    def __init__(self, host: str, org: str, repo: str, branch: str):
        self.api = GiteaRepositoryApi(host=host, org=org, repo=repo)
        branch_id = self.api.get_branch_id(branch)
        self.filepaths: tuple[str, ...] = self.api.get_branch_filepaths(branch_id)

    async def _write_filepath_cksum(
        self, filepath: str, content: bytes, cksum_file: str, cksum_file_lock: asyncio.Lock
    ):
        async with cksum_file_lock, aiofiles.open(filepath, "a") as f:
            cksum = sha256(content).hexdigest()
            await f.write(f"{filepath}\t{cksum}\n")

    async def _save_filepath_content(
        self,
        root_dir: Path,
        filepath: str,
        n_tasks_sem: asyncio.Semaphore,
        cksum_file: str | None = None,
        cksum_file_lock: asyncio.Lock | None = None,
    ):
        logging.log(level=logging.INFO, msg=f"Fetching {filepath}...")

        if cksum_file and not cksum_file_lock:
            raise ValueError("`cksum_file` and `cksum_file_lock` must only be specified conjointly")

        await n_tasks_sem.acquire()

        local_filepath = root_dir / filepath
        parent_dir = root_dir / Path(filepath).parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True)

        async with aiofiles.open(local_filepath, "w") as f:
            content = await self.api.get_file_content(filepath)
            await f.write(content.decode())

        if cksum_file and cksum_file_lock:
            await self._write_filepath_cksum(filepath, content, cksum_file, cksum_file_lock)

        n_tasks_sem.release()

    async def _save_contents_with_cksums(self, root_dir: Path, cksum_file: Path, n_tasks_sem: asyncio.Semaphore):
        if cksum_file.exists():
            cksum_file.unlink()
        cksum_file_lock = asyncio.Lock()

        tasks = (
            asyncio.create_task(
                self._save_filepath_content(
                    root_dir=root_dir,
                    filepath=filepath,
                    cksum_file=str(cksum_file),
                    cksum_file_lock=cksum_file_lock,
                    n_tasks_sem=n_tasks_sem,
                )
            )
            for filepath in self.filepaths
        )
        await asyncio.gather(*tasks)

    async def _save_contents(self, root_dir: Path, n_tasks_sem: asyncio.Semaphore):
        tasks = (
            asyncio.create_task(
                self._save_filepath_content(
                    root_dir=root_dir,
                    filepath=filepath,
                    n_tasks_sem=n_tasks_sem,
                )
            )
            for filepath in self.filepaths
        )
        await asyncio.gather(*tasks)

    async def save_contents(self, root_dir: str | Path, n_tasks_max: int, cksum_file: str | None = None):
        root_dir = Path(root_dir)
        if not root_dir.exists():
            root_dir.mkdir(parents=True)

        n_tasks_sem = asyncio.Semaphore(n_tasks_max)
        if cksum_file:
            await self._save_contents_with_cksums(root_dir, Path(cksum_file), n_tasks_sem)
        else:
            await self._save_contents(root_dir, n_tasks_sem)
