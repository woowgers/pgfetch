from typing import Self, TypeAlias, Sequence

import pytest
from project.giteaapi import GiteaRepositoryBranchApi
from project.fetcher import GiteaRepositoryBranchFetcher

from project.types import GitBranch, GitEntry, GitTree


JSON: TypeAlias = dict | Sequence[dict]


class MockResponse:
    def __init__(self, status_code: int, json: JSON | None = None):
        self.status_code = status_code
        self._json: JSON = json or {}

    def json(self) -> JSON:
        return self._json


class MockAsyncResponse:
    def __init__(self, status_code: int, json: JSON | None = None):
        self.status_code = status_code
        self._json: JSON = json or {}

    async def json(self) -> JSON:
        return self._json

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_):
        pass


@pytest.fixture
def api() -> GiteaRepositoryBranchApi:
    return GiteaRepositoryBranchApi(host='host', org='org', repo='repo', branch='branch')


@pytest.fixture
def expected_branches_list_url(api: GiteaRepositoryBranchApi) -> str:
    base_url = f"https://{api.host}/api/v1"
    return f"{base_url}/repos/{api.org}/{api.repo}/branches"


@pytest.fixture
def raw_branch(api: GiteaRepositoryBranchApi) -> dict:
    return {
        "name": api.branch,
        "commit": { "id": "fj0239fj2039jf0" }
    }


@pytest.fixture
def raw_unexpected_branch() -> dict:
    return {
        "name": "dev",
        "commit": { "id": "20fj209jf3023j" }
    }


@pytest.fixture
def raw_branches(raw_branch: dict, raw_unexpected_branch: dict) -> Sequence[dict]:
    return (raw_branch, raw_unexpected_branch)


@pytest.fixture
def expected_branches(raw_branches: Sequence[dict]) -> Sequence[GitBranch]:
    return tuple(GitBranch.parse_from_raw(raw_branch) for raw_branch in raw_branches)


@pytest.fixture
def raw_branches_without_expected_branch(raw_unexpected_branch: dict) -> Sequence[dict]:
    return (raw_unexpected_branch,)


@pytest.fixture
def branches_without_expected_branch(raw_branches_without_expected_branch: Sequence[dict]) -> Sequence[GitBranch]:
    return tuple(GitBranch.parse_from_raw(raw_branch) for raw_branch in raw_branches_without_expected_branch)


@pytest.fixture
def expected_branch(raw_branch: GitBranch) -> GitBranch:
    return GitBranch.parse_from_raw(raw_branch)


@pytest.fixture
def expected_branch_tree_url(api: GiteaRepositoryBranchApi, expected_branch: GitBranch) -> str:
    base_url = f"https://{api.host}/api/v1"
    return f"{base_url}/repos/{api.org}/{api.repo}/git/trees/{expected_branch.id}?recursive=true"


@pytest.fixture
def raw_file_entry() -> dict:
    return {
        "path": "path/to/file",
        "type": "blob"
    }


@pytest.fixture
def file_entry(raw_file_entry: dict) -> GitEntry:
    return GitEntry(path=raw_file_entry["path"], is_file=raw_file_entry["type"] == "blob")


@pytest.fixture
def expected_file_content_url(api: GiteaRepositoryBranchApi, file_entry: GitEntry, expected_branch: GitBranch) -> str:
    base_url = f"https://{api.host}/api/v1"
    return f"{base_url}/repos/{api.org}/{api.repo}/contents/{file_entry.path}?ref={expected_branch.name}"


@pytest.fixture
@pytest.mark.asyncio
async def fetcher(api: GiteaRepositoryBranchApi) -> GiteaRepositoryBranchFetcher:
    ...


@pytest.fixture
def raw_dir_entry() -> dict:
    return {
        "path": "path/to/directory",
        "type": "tree"
    }


@pytest.fixture
def file_entries(file_entry: GitEntry) -> tuple[GitEntry, ...]:
    return (file_entry,)


@pytest.fixture
def raw_entries(raw_file_entry: dict, raw_dir_entry: dict) -> Sequence[dict]:
    return (
        raw_file_entry,
        raw_dir_entry
    )


@pytest.fixture
def entries(raw_entries: Sequence[dict]) -> tuple[GitEntry, ...]:
    return tuple(GitEntry.parse_from_raw(raw_entry) for raw_entry in raw_entries)


@pytest.fixture
def dir_entry(raw_file_entry: dict) -> GitEntry:
    return GitEntry.parse_from_raw(raw_file_entry)


@pytest.fixture
def expected_raw_tree(raw_file_entry: dict, raw_dir_entry: dict) -> dict:
    return {
        "tree": (
            raw_file_entry,
            raw_dir_entry
        )
    }


@pytest.fixture
def expected_tree(expected_raw_tree: dict) -> GitTree:
    return GitTree.parse_from_raw(expected_raw_tree)
