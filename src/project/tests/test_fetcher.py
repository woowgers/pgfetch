from unittest.mock import patch

import pytest

from ..fetcher import RepositoryFileFetcher


class TestWriteFile:
    @pytest.fixture
    async def test_writes_file_with_expected_content(self):
        ...

    @pytest.fixture
    async def test_writes_cksum_in_expected_format(self):
        ...


class TestSaveFileContent:
    @pytest.fixture
    async def test_saves_file_content(self):
        ...


class TestSaveContents:
    @pytest.fixture
    async def test_saves_content(self):
        ...
