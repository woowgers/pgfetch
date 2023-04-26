from typing import Sequence

import pytest

from ..types import GitBranch, GitEntry, GitTree


@pytest.mark.skip
class TestBranch:
    def test_parse_from_raw_parses_as_expected(self, raw_branch: dict, expected_branch: GitBranch):
        assert GitBranch.parse_from_raw(raw_branch) == expected_branch


@pytest.mark.skip
class TestGitEntry:
    def test_parse_from_raw_parses_as_expected(self, raw_file_entry: dict, file_entry: GitEntry):
        assert GitEntry.parse_from_raw(raw_file_entry) == file_entry

    def test_is_file_if_file(self, file_entry: GitEntry):
        assert file_entry.is_file == True

    def test_not_is_file_if_not_file(self, dir_entry: GitEntry):
        assert dir_entry.is_file == False


@pytest.mark.skip
class TestGitTree:
    def test_parse_from_raw_parses_as_expected(self, expected_raw_tree: dict, expected_tree: GitTree):
        assert GitTree.parse_from_raw(expected_raw_tree) == expected_tree

    def test_files_returns_only_file_entries(self, expected_raw_tree: dict, file_entries: Sequence[GitEntry]):
        tree = GitTree.parse_from_raw(expected_raw_tree)
        assert set(tree.files) == set(file_entries)
