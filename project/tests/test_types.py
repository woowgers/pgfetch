from pathlib import Path
from typing import Sequence

from ..types import GitBranch, GitEntry, GitTree


class TestBranch:
    def test_parse_from_raw_parses_as_expected(self, raw_branch: dict, expected_branch: GitBranch):
        branch = GitBranch.parse_from_raw(raw_branch)
        assert branch == expected_branch


class TestGitEntry:
    def test_parse_from_raw_parses_as_expected(self, raw_file_entry: dict, file_entry: GitEntry):
        entry = GitEntry.parse_from_raw(raw_file_entry)
        assert entry == file_entry

    def test_is_file_if_file(self, raw_file_entry: dict):
        entry = GitEntry.parse_from_raw(raw_file_entry)
        assert entry.is_file == True

    def test_not_is_file_if_not_file(self, raw_dir_entry: dict):
        entry = GitEntry.parse_from_raw(raw_dir_entry)
        assert entry.is_file == False


class TestGitTree:
    # def test_parse_from_raw_parses_as_expected(sef, raw_tree: dict, )

    def test_entries_returns_all_entries(self, raw_tree: dict, entries: Sequence[GitEntry]):
        tree = GitTree.parse_from_raw(raw_tree)
        assert len(tree.entries) == len(entries)

    def test_files_returns_only_file_entries(self, raw_tree: dict, file_entries: Sequence[GitEntry]):
        tree = GitTree.parse_from_raw(raw_tree)
        assert set(tree.files) == set(file_entries)
