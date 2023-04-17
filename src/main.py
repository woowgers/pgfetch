import asyncio
import sys
from os.path import basename

from fetcher import RepositoryFilepathFetcher


async def main_async():
    fetcher = RepositoryFilepathFetcher(
        host="gitea.radium.group/api/v1", org="radium", repo="project-configuration", branch="master"
    )
    await fetcher.list_all_contents_async()


def main():
    fetcher = RepositoryFilepathFetcher(
        host="gitea.radium.group/api/v1", org="radium", repo="project-configuration", branch="master"
    )
    fetcher.list_all_contents()


if __name__ == "__main__":
    OPTIONS = ("async", "sync")

    def help():
        print(f"Usage: python {basename(__file__)} < async | sync >")
        exit()

    if len(sys.argv) != 2 or sys.argv[1] not in OPTIONS:
        help()

    if sys.argv[1] == "async":
        asyncio.run(main_async())
    else:
        main()
