from pathlib import Path

import pytest

from project.types import GitEntry

from ..fetcher import GiteaRepositoryBranchFetcher


class TestWriteFileContent:
    @pytest.mark.asyncio
    async def test_writes_file_with_expected_content(
        self, fetcher: GiteaRepositoryBranchFetcher, tmp_path: Path, file_entry: GitEntry, content_text: str
    ):
        local_filepath = tmp_path / file_entry.path
        await fetcher._write_file_content(local_filepath, content_text)
        assert local_filepath.read_text() == content_text

    @pytest.mark.asyncio
    async def test_rewrites_file_if_exists(
        self, fetcher: GiteaRepositoryBranchFetcher, tmp_path: Path, file_entry: GitEntry, content_text: str
    ):
        local_filepath = tmp_path / file_entry.path
        local_filepath.parent.mkdir(parents=True, exist_ok=True)
        local_filepath.write_text("some unexpected content")
        await fetcher._write_file_content(local_filepath, content_text)
        assert local_filepath.read_text() == content_text


class TestFetchFile:
    ...


class TestFetchFiles:
    ...
