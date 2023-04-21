import asyncio
import random
from base64 import b64encode
from hashlib import sha256
from pathlib import Path
from unittest.mock import call, patch

import pytest

from project.types import FileContent, GitEntry, GitTree

from ..fetcher import RepositoryFileFetcher


# ROOT_DIR =


@pytest.fixture
def fetcher() -> RepositoryFileFetcher:
    return RepositoryFileFetcher("host", "org", "repo", "branch")


@pytest.fixture
def root_dir() -> Path:
    return Path("root/dir/")


@pytest.fixture
def expected_raw_file_entry() -> dict:
    return {"path": "path/to/file", "type": "blob"}


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


REMOTE_FILEPATH = Path("path/to/file")
INITIAL_CONTENT = "some initial content, which is cksums"
CONTENT_TEXT = "some content"
CONTENT_BYTES = CONTENT_TEXT.encode()
CONTENT_B64 = b64encode(CONTENT_BYTES).decode()


@pytest.fixture
def expected_raw_content() -> dict:
    return {"content": CONTENT_B64}


@pytest.fixture
def expected_content(expected_raw_content: dict) -> FileContent:
    return FileContent(expected_raw_content)


@pytest.fixture
def expected_tree(expected_raw_tree: dict) -> GitTree:
    return GitTree(expected_raw_tree)


@pytest.fixture
def cksum_file_expected_content(expected_file_entry: GitEntry, expected_content: FileContent) -> str:
    cksum = sha256(expected_content.bytes).hexdigest()
    return f"{expected_file_entry.path}\t{cksum}\n"


class TestWriteFileContent:
    @pytest.mark.asyncio
    async def test_writes_file_with_expected_content(
        self, fetcher: RepositoryFileFetcher, tmp_path: Path, expected_file_entry: GitEntry
    ):
        local_filepath = tmp_path / expected_file_entry.path
        await fetcher._write_file_content(local_filepath, CONTENT_BYTES)
        assert local_filepath.read_text() == CONTENT_TEXT

    @pytest.mark.asyncio
    async def test_rewrites_file_if_exists(
        self, fetcher: RepositoryFileFetcher, tmp_path: Path, expected_file_entry: GitEntry
    ):
        local_filepath = tmp_path / expected_file_entry.path
        local_filepath.parent.mkdir(parents=True, exist_ok=True)
        local_filepath.write_text("some unexpected content")
        await fetcher._write_file_content(local_filepath, CONTENT_BYTES)
        assert local_filepath.read_text() == CONTENT_TEXT


class TestWriteFileCksum:
    @pytest.mark.asyncio
    async def test_craetes_cksum_file_if_doesnt_exist(
        self, fetcher: RepositoryFileFetcher, expected_file_entry: GitEntry, tmp_path: Path
    ):
        cksum_file = tmp_path / "sha256sums"
        await fetcher._write_file_cksum(expected_file_entry.path, CONTENT_BYTES, cksum_file, asyncio.Lock())
        assert cksum_file.exists()

    @pytest.mark.asyncio
    async def test_writes_cksum_in_expected_format(
        self,
        fetcher: RepositoryFileFetcher,
        expected_file_entry: GitEntry,
        tmp_path: Path,
        cksum_file_expected_content: str,
    ):
        cksum_file = tmp_path / "sha256sums"
        await fetcher._write_file_cksum(expected_file_entry.path, CONTENT_BYTES, cksum_file, asyncio.Lock())
        assert cksum_file.read_text() == cksum_file_expected_content

    @pytest.mark.asyncio
    async def test_appends_cksum_after_existing_content(
        self,
        fetcher: RepositoryFileFetcher,
        expected_file_entry: GitEntry,
        tmp_path: Path,
        cksum_file_expected_content: str,
    ):
        cksum_file = tmp_path / "sha256sums"
        cksum_file.write_text(INITIAL_CONTENT)
        await fetcher._write_file_cksum(expected_file_entry.path, CONTENT_BYTES, cksum_file, asyncio.Lock())
        assert cksum_file.read_text() == INITIAL_CONTENT + cksum_file_expected_content


class TestSaveFileToLocalDir:
    @pytest.mark.asyncio
    async def test_calls_write_content_and_write_cksum_with_expected_arguments(
        self,
        fetcher: RepositoryFileFetcher,
        expected_content: FileContent,
        tmp_path: Path,
        expected_file_entry: GitEntry,
    ):
        with (
            patch("project.giteaapi.GiteaRepositoryApi.get_file_content") as get_file_content,
            patch("project.fetcher.RepositoryFileFetcher._write_file_cksum") as write_file_cksum,
            patch("project.fetcher.RepositoryFileFetcher._write_file_content") as write_file_content,
        ):
            get_file_content.return_value = expected_content
            local_filepath = tmp_path / expected_file_entry.path
            cksum_file = Path("sha256sums")
            lock = asyncio.Lock()
            sem = asyncio.Semaphore()
            await fetcher.save_file_to_local_dir(expected_file_entry.path, tmp_path, cksum_file, lock, sem)
            assert write_file_cksum.call_args == call(expected_file_entry.path, CONTENT_BYTES, cksum_file, lock)
            assert write_file_content.call_args == call(local_filepath, CONTENT_BYTES)


class TestSaveContents:
    ...


class TestContstructTaks:
    @patch("project.fetcher.RepositoryFileFetcher._construct_tasks")
    def construct_tasks(self, *args) -> tuple:
        return args

    @patch("project.fetcher.RepositoryFileFetcher.save_file_to_local_dir")
    @pytest.mark.asyncio
    async def save_file_to_local_dir(self, *args) -> tuple:
        return args

    @pytest.mark.asyncio
    def test_calls_construct_tasks_with_expected_arguments(self, fetcher: RepositoryFileFetcher, expected_tree: GitTree, root_dir: Path):
        ...
