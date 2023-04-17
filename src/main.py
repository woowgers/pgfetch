from base64 import b64decode
from hashlib import sha256
from itertools import repeat
from multiprocessing import Manager, Lock, Process
from multiprocessing.pool import AsyncResult, Pool
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

N_PROCESSES = 3


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
    result: AsyncResult = api.repo_get_contents(owner=owner, repo=repo, filepath=filepath, async_req=True)  # type: ignore
    raw_content: ContentsResponse = result.get()
    if raw_content.content is None:
        raise RuntimeError(f"Failed to get {filepath} content")
    if raw_content.type != "file":
        raise RuntimeError(f"Unexpected content type (expected 'file', got {raw_content.type})")
    if raw_content.encoding != "base64":
        raise RuntimeError(f"Unexpected content encoding (expected 'base64', got {raw_content.encoding})")

    content = b64decode(raw_content.content)

    return content


def write_filepath_sha256sum(filepath: Path, dir: TemporaryDirectory, lock) -> None:
    content = get_filepath_content(api, owner=REPO_ORG, repo=REPO_NAME, filepath=str(filepath))
    sha_sum = sha256(content).hexdigest()
    parent_dir = dir.name / filepath.parent
    local_filepath = dir.name / filepath
    if not parent_dir.exists():
        parent_dir.mkdir(parents=True)
    with open(local_filepath, "w") as f:
        f.write(content.decode())
    with lock, open(SUMS_FILE, "a") as f:
        f.write(f"{filepath}\t{sha_sum}\n")


def write_sums(filepaths: tuple[Path]) -> None:
    if SUMS_FILE.exists():
        SUMS_FILE.unlink()

    directory = TemporaryDirectory()
    lock = Lock()
    for i in range(len(filepaths)):
        process = Process(target=write_filepath_sha256sum, args=(filepaths[i], directory, lock))
        process.start()
        process.join()

    """ Should be this, but seems like giteapy doesn't like it... """
    # with Pool(processes=N_PROCESSES) as pool:
    #     lock = Manager().Lock()
    #     pool.starmap(write_filepath_sha256sum, zip(filepaths, repeat(directory), repeat(lock)))


if __name__ == "__main__":
    configuration = Configuration()
    configuration.host = REPO_HOST
    api = RepositoryApi(ApiClient(configuration=configuration))

    branch_id = get_branch_id(api, *REPO_SPEC)
    filepaths = get_branch_filepaths(api, *REPO_SPEC)
    write_sums(filepaths)
