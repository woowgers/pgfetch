import asyncio
import os
from tempfile import TemporaryDirectory

from fetcher import RepositoryFileFetcher


async def main():
    fetcher = RepositoryFileFetcher(host="gitea.radium.group", org="radium", repo="flatfilecms", branch="master")
    tmpdir = TemporaryDirectory()
    await fetcher.save_contents(root_dir=tmpdir.name, cksum_file="sha256sums", n_tasks_max=10)
    print(*tuple(os.walk(tmpdir.name)))


if __name__ == "__main__":
    asyncio.run(main())
