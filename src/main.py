from base64 import b64decode
from pathlib import Path
from hashlib import sha256

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


def get_branch_id(api: RepositoryApi, owner: str, repo: str, branch: str) -> str:
    raw_branch = api.repo_get_branch(owner=owner, repo=repo, branch=branch)
    if not isinstance(raw_branch, Branch):
        raise RuntimeError("Unexpected SDK return value")
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

    raw_tree = api.get_tree(owner=owner, repo=repo, sha=branch_id, recursive=True, page=1)
    if not isinstance(raw_tree, GitTreeResponse):
        raise RuntimeError("Unexpected SDK return value")
    if raw_tree.tree is None:
        raise RuntimeError("Failed to fetch repository tree")

    files_entries = filter(entry_is_regular_file, raw_tree.tree)
    filepath_tuple = tuple(map(entry_get_filepath, files_entries))

    return filepath_tuple


def get_filepath_content(api: RepositoryApi, owner: str, repo: str, filepath: str) -> bytes:
    raw_content = api.repo_get_contents(owner=owner, repo=repo, filepath=filepath)
    if not isinstance(raw_content, ContentsResponse):
        raise RuntimeError("Unexpected SDK return value")
    if raw_content.content is None:
        raise RuntimeError(f"Failed to get {filepath} content")
    if raw_content.type != "file":
        raise RuntimeError(f"Unexpected content type (expected 'file', got {raw_content.type})")
    if raw_content.encoding != "base64":
        raise RuntimeError(f"Unexpected content encoding (expected 'base64', got {raw_content.encoding})")

    content = b64decode(raw_content.content)

    return content


if __name__ == "__main__":
    configuration = Configuration()
    configuration.host = REPO_HOST
    api = RepositoryApi(ApiClient(configuration=configuration))

    branch_id = get_branch_id(api, *REPO_SPEC)
    filepaths = get_branch_filepaths(api, *REPO_SPEC)

    if SUMS_FILE.exists():
        SUMS_FILE.unlink()

    with open(SUMS_FILE, "w") as f:
        for filepath in filepaths:
            content = get_filepath_content(api, owner=REPO_ORG, repo=REPO_NAME, filepath=str(filepath))
            sha_sum = sha256(content).hexdigest()
            f.write(f"{filepath}\t{sha_sum}\n")
