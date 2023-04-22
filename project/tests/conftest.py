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
@pytest.mark.asyncio
async def fetcher(api: GiteaRepositoryBranchApi) -> GiteaRepositoryBranchFetcher:
    ...


@pytest.fixture
def raw_branch() -> dict:
    return {
        "name": "master",
        "commit": { "id": "fj0239fj2039jf0" }
    }


@pytest.fixture
def expected_branch(raw_branch: GitBranch) -> GitBranch:
    return GitBranch.parse_from_raw(raw_branch)


@pytest.fixture
def raw_file_entry() -> dict:
    return {
        "path": "path/to/file",
        "type": "blob"
    }

@pytest.fixture
def raw_dir_entry() -> dict:
    return {
        "path": "path/to/directory",
        "type": "tree"
    }

@pytest.fixture
def file_entry(raw_file_entry: dict) -> GitEntry:
    return GitEntry(path=raw_file_entry["path"], is_file=raw_file_entry["type"] == "blob")


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
    return GitEntry(path=raw_file_entry["path"], is_file=raw_file_entry["type"] == "blob")


@pytest.fixture
def raw_tree(raw_file_entry: dict, raw_dir_entry: dict) -> dict:
    return {
        "tree": (
            raw_file_entry,
            raw_dir_entry
        )
    }


@pytest.fixture
def expected_tree(file_entry: GitEntry, dir_entry: GitEntry) -> GitTree:
    return GitTree((file_entry, dir_entry))
