from base64 import b64encode
from pathlib import Path
from typing import Sequence
import pytest

from ..types import FileContent, GitBranch, GitEntry, GitTree


class TestBranch:
    @pytest.fixture
    def branch_id(self) -> str:
        return "eb4dc314435649737ad343ef82240b96256d5eb8"

    @pytest.fixture
    def branch_name(self) -> str:
        return "master"

    @pytest.fixture
    def raw_branch(self, branch_name: str, branch_id: int) -> dict:
        return {"name": branch_name, "commit": {"id": branch_id}}

    def test_id_returns_branch_id(self, raw_branch: dict, branch_id: str):
        branch = GitBranch(raw_branch)
        assert branch.id == branch_id

    def test_name_returns_branch_name(self, branch_name: str, raw_branch: dict):
        branch = GitBranch(raw_branch)
        assert branch.name == branch_name


class TestFileContent:
    @pytest.fixture
    def content_text(self) -> str:
        return "sample text"

    @pytest.fixture
    def content_bytes(self, content_text: str) -> bytes:
        return content_text.encode()

    @pytest.fixture
    def content_b64encoded(self, content_bytes: bytes) -> str:
        return b64encode(content_bytes).decode()

    @pytest.fixture
    def raw_content_response(self, content_b64encoded: str) -> dict:
        return { "content": content_b64encoded }

    def test_content_returns_encoded_content(self, raw_content_response: dict, content_b64encoded: str):
        content = FileContent(raw_content_response)
        assert content.content == content_b64encoded

    def test_bytes_returns_decoded_bytes(self, raw_content_response: dict, content_bytes: bytes):
        content = FileContent(raw_content_response)
        assert content.bytes == content_bytes

    def test_text_returns_decoded_text(self, raw_content_response: dict, content_text: str):
        content = FileContent(raw_content_response)
        assert content.text == content_text


class TestGitEntry:
    @pytest.fixture
    def entry_path(self) -> Path:
        return Path("/path/to/entry")

    @pytest.fixture
    def raw_file_entry(self, entry_path: Path) -> dict:
        return { "path": str(entry_path), "type": "blob" }

    @pytest.fixture
    def raw_dir_entry(self, entry_path: Path) -> dict:
        return { "path": str(entry_path), "type": "tree" }

    def test_path_returns_path(self, raw_file_entry: dict, entry_path: Path):
        entry = GitEntry(raw_file_entry)
        assert entry.path == entry_path

    def test_is_file_if_file(self, raw_file_entry: dict):
        entry = GitEntry(raw_file_entry)
        assert entry.is_file == True

    def test_not_is_file_if_not_file(self, raw_dir_entry: dict):
        entry = GitEntry(raw_dir_entry)
        assert entry.is_file == False


class TestGitTree:
    @pytest.fixture
    def raw_file_entry(self) -> dict:
        return {
            "path": "path",
            "type": "blob"
        }

    @pytest.fixture
    def raw_dir_entry(self) -> dict:
        return {
            "path": "path",
            "type": "file"
        }

    @pytest.fixture
    def raw_entries(self, raw_file_entry: dict, raw_dir_entry: dict) -> Sequence[dict]:
        return (raw_file_entry, raw_dir_entry)

    @pytest.fixture
    def raw_tree(self, raw_entries: Sequence[dict]) -> dict:
        return { "tree": raw_entries }

    @pytest.fixture
    def entries(self, raw_entries: Sequence[dict]) -> Sequence[GitEntry]:
        return tuple(map(GitEntry, raw_entries))

    @pytest.fixture
    def file_entries(self, raw_file_entry: dict) -> Sequence[GitEntry]:
        return (GitEntry(raw_file_entry),)

    def test_entries_returns_all_entries(self, raw_tree: dict, entries: Sequence[GitEntry]):
        tree = GitTree(raw_tree)
        assert len(tree.entries) == len(entries)

    def test_files_returns_only_file_entries(self, raw_tree: dict, file_entries: Sequence[GitEntry]):
        tree = GitTree(raw_tree)
        assert set(tree.files) == set(file_entries)
