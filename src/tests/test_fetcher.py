from unittest.mock import patch

import pytest

from ..fetcher import RepositoryFileFetcher


class TestRemoveCksumFileIfExists:
    def test_removes_cksum_file_if_exists(self):
        ...

    def test_does_nothing_if_doesnt_exist(self):
        ...


class TestWriteFile:
    def test_writes_file_with_expected_content(self):
        ...

    def test_writes_cksum_in_expected_format(self):
        ...


class TestSaveFileContent:
    def test_saves_file_content(self):
        ...


class TestSaveContents:
    def test_saves_content(self):
        ...
