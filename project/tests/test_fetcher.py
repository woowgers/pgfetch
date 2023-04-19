import asyncio
from base64 import b64encode
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

import pytest

from project.giteaapi import GiteaRepositoryApi
from project.types import FileContent, GitEntry, GitTree

from ..fetcher import RepositoryFileFetcher


@pytest.fixture
def fetcher() -> RepositoryFileFetcher:
    return RepositoryFileFetcher("host", "org", "repo", "branch")


@pytest.fixture
def root_dir() -> Path:
    return Path("root/dir/")


@pytest.fixture
def expected_raw_file_entry() -> dict:
    return {"path": "/path/to/file", "type": "blob"}


@pytest.fixture
def expected_file_entry(expected_raw_file_entry: dict) -> GitEntry:
    return GitEntry(expected_raw_file_entry)


@pytest.fixture
def expected_raw_tree(expected_raw_file_entry: dict) -> dict:
    return {
        "tree": (
            expected_raw_file_entry,
            {"path": "/path/to/directory", "type": "tree"},
        )
    }


CONTENT = b64encode("some content".encode()).decode()


@pytest.fixture
def expected_raw_content() -> dict:
    return {"content": CONTENT}


@pytest.fixture
def expected_content(expected_raw_content: dict) -> FileContent:
    return FileContent(expected_raw_content)


@pytest.fixture
def expected_tree(expected_raw_tree: dict) -> GitTree:
    return GitTree(expected_raw_tree)

@pytest.fixture
def cksum_file_initial_content() -> str:
    return f"initial content"


@pytest.fixture
def cksum_file_expected_content(expected_file_entry: GitEntry, expected_content: FileContent) -> str:
    cksum = sha256(expected_content.bytes).hexdigest()
    return f"{expected_file_entry.path}\t{cksum}"


class TestWriteFileContentAndCksum:
    @pytest.mark.asyncio
    async def test_writes_file_with_expected_content(self,  expected_tree: GitTree):
        with patch("project.giteaapi.GiteaRepositoryApi.get_branch_tree") as get_branch_tree:
            get_branch_tree.return_value = expected_tree
            ...

    @pytest.mark.asyncio
    async def test_writes_cksum_in_expected_format(self):
        ...


class TestSaveFileToLocalDir:
    @pytest.mark.asyncio
    async def test_saves_file_to_local_dir(self):
        ...


class TestSaveContents:
    @pytest.mark.asyncio
    async def test_rewrites_cksums_file_if_exists(self):
        with (
            patch("project.giteaapi.GiteaRepositoryApi.get_branch_tree") as get_branch_tree,
            patch("project.fetcher.RepositoryFileFetcher.save_file_to_local_dir") as save_file,
        ):
            ...

    @pytest.mark.asyncio
    async def test_saves_content(self):
        ...
