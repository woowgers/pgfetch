import asyncio
import logging
import os
import sys
from tempfile import TemporaryDirectory

from project.fetcher import RepositoryFileFetcher


def configure_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


async def main():
    cksum_file = "sha256sums"

    fetcher = RepositoryFileFetcher(
        host="gitea.radium.group", org="radium", repo="project-configuration", branch="master"
    )
    tmpdir = TemporaryDirectory()
    await fetcher.fetch_files(root_dir=tmpdir.name)

    logging.info(f"saved checksums to {cksum_file}")
    logging.info(f"{tmpdir.name} content: " +  "\n".join(map(str, os.walk(tmpdir.name))))


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
