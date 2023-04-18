import asyncio
import logging
import os
import sys
from tempfile import TemporaryDirectory

from fetcher import RepositoryFileFetcher


def configure_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


async def main():
    fetcher = RepositoryFileFetcher(
        host="gitea.radium.group", org="radium", repo="flatfilecms", branch="master"
    )
    tmpdir = TemporaryDirectory()
    await fetcher.save_contents(root_dir=tmpdir.name, cksum_file="sha256sums")
    print(*tuple(os.walk(tmpdir.name)))


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
