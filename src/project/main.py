import asyncio
import logging
import os
import sys
from base64 import b64encode
from pathlib import Path
from tempfile import TemporaryDirectory

import aiohttp

from project.api.gitea import GiteaRepositoryBranch, GiteaRepositoryBranchApi
from project.fetcher import RepositoryBranchFetcher


def configure_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


async def fetch_repo_branch(root_dir: Path) -> None:
    session = aiohttp.ClientSession()
    branch = GiteaRepositoryBranch(host="gitea.radium.group", org="radium", repo="project-configuration", name="master")
    api_connector = GiteaRepositoryBranchApi(session=session, branch=branch)
    fetcher = RepositoryBranchFetcher(api=api_connector)

    async with session:
        await fetcher.fetch_files(root_dir=root_dir)


def write_dir_checksum_to_file(root_dir: Path, checksums_file: Path) -> None:
    with checksums_file.open("w") as f:
        for filepath in filter(Path.is_file, root_dir.glob("**/*")):
            checksum = b64encode(filepath.read_bytes()).decode()
            f.write(f"{filepath}\t{checksum}\n")

    logging.info(f"saved checksums to {checksums_file}")
    logging.info(f"{root_dir} content: " + "\n".join(map(str, os.walk(root_dir))))


async def main():
    tmpdir = TemporaryDirectory()
    checksums_file = Path("sha256sums")
    await fetch_repo_branch(Path(tmpdir.name))
    write_dir_checksum_to_file(Path(tmpdir.name), checksums_file)


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
