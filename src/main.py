import asyncio
from base64 import b64decode
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from giteapy import (
    ApiClient,
    Branch,
    Configuration,
    ContentsResponse,
    GitEntry,
    GitTreeResponse,
    RepositoryApi,
)

REPO_HOST = "https://gitea.radium.group/api/v1"
REPO_ORG = "radium"
REPO_NAME = "project-configuration"
REPO_BRANCH = "master"
REPO_SPEC = (REPO_ORG, REPO_NAME, REPO_BRANCH)

SUMS_FILE = Path("sha256sums")

N_WORKERS = 3


def get_branch_id(api: RepositoryApi, owner: str, repo: str, branch: str) -> str:
    raw_branch: Branch = api.repo_get_branch(owner=owner, repo=repo, branch=branch)  # type: ignore
    if raw_branch.commit is None:
        raise RuntimeError(f"No commits in branch `{branch}`")

    return raw_branch.commit.id


def get_branch_filepaths(api: RepositoryApi, owner: str, repo: str, branch_id: str) -> tuple[Path, ...]:
    def entry_get_filepath(entry: GitEntry) -> Path:
        if entry.path is None:
            raise RuntimeError("Entry doesn't have name")
        return Path(entry.path)

    def entry_is_regular_file(entry: GitEntry) -> bool:
        return entry.type == "blob"

    raw_tree: GitTreeResponse = api.get_tree(owner=owner, repo=repo, sha=branch_id, recursive=True, page=1)  # type: ignore
    if raw_tree.tree is None:
        raise RuntimeError("Failed to fetch repository tree")

    files_entries = filter(entry_is_regular_file, raw_tree.tree)
    filepath_tuple = tuple(map(entry_get_filepath, files_entries))

    return filepath_tuple


def get_filepath_content(api: RepositoryApi, owner: str, repo: str, filepath: str) -> bytes:
    content_response: ContentsResponse = api.repo_get_contents(owner=owner, repo=repo, filepath=filepath)  # type: ignore
    if content_response.content is None:
        raise RuntimeError(f"Failed to get {filepath} content")
    if content_response.type != "file":
        raise RuntimeError(f"Unexpected content type (expected 'file', got {content_response.type})")
    if content_response.encoding != "base64":
        raise RuntimeError(f"Unexpected content encoding (expected 'base64', got {content_response.encoding})")

    content = b64decode(content_response.content)

    return content


async def write_filepath_sha256sum(
    api: RepositoryApi,
    filepath: Path,
    dir: TemporaryDirectory,
    sums_file_lock: asyncio.Lock,
    n_tasks_sem: asyncio.Semaphore,
) -> None:
    async with n_tasks_sem:
        content = get_filepath_content(api, owner=REPO_ORG, repo=REPO_NAME, filepath=str(filepath))
        sha_sum = sha256(content).hexdigest()
        parent_dir = dir.name / filepath.parent
        local_filepath = dir.name / filepath
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True)
        with open(local_filepath, "w") as f:
            f.write(content.decode())
        with open(SUMS_FILE, "a") as f:
            async with sums_file_lock:
                f.write(f"{filepath}\t{sha_sum}\n")


async def write_sums(api: RepositoryApi, filepaths: tuple[Path]) -> None:
    if SUMS_FILE.exists():
        SUMS_FILE.unlink()

    directory = TemporaryDirectory()
    n_tasks_sem = asyncio.Semaphore(N_WORKERS)
    sums_file_lock = asyncio.Lock()
    tasks = (
        asyncio.create_task(write_filepath_sha256sum(api, filepath, directory, sums_file_lock, n_tasks_sem))
        for filepath in filepaths
    )
    await asyncio.gather(*tasks)


async def main():
    configuration = Configuration()
    configuration.host = REPO_HOST
    api = RepositoryApi(ApiClient(configuration=configuration))

    filepaths = get_branch_filepaths(api, *REPO_SPEC)
    await write_sums(api, filepaths)


if __name__ == "__main__":
    asyncio.run(main())
