import pytest

from ..types import FileContent, GitBranch


class TestBranch:
    branch_name: str = "master"
    branch_id: str = "eb4dc314435649737ad343ef82240b96256d5eb8"

    @pytest.fixture
    def raw_branch(self) -> dict:
        return {"name": self.branch_name, "commit": {"id": self.branch_id}}

    def test_id_returns_branch_id(self, raw_branch: dict):
        branch = GitBranch(raw_branch)
        assert branch.id == self.branch_id

    def test_name_returns_branch_name(self, raw_branch: dict):
        branch = GitBranch(raw_branch)
        assert branch.name == self.branch_name


class TestFileContent:
    content_text = "sample text"
    content_bytes = b"sample text"
    content_b64encoded = "c2FtcGxlIHRleHQ="

    @pytest.fixture
    def raw_content_response(self) -> dict:
        return { "content": self.content_b64encoded }

    def test_content_returns_encoded_content(self, raw_content_response: dict):
        content = FileContent(raw_content_response)
        assert content.content == self.content_b64encoded

    def test_bytes_returns_decoded_bytes(self, raw_content_response: dict):
        content = FileContent(raw_content_response)
        assert content.bytes == self.content_bytes

    def test_text_returns_decoded_text(self, raw_content_response: dict):
        content = FileContent(raw_content_response)
        assert content.text == self.content_text


class TestGitEntry:
    def test_path_returns_path(self):
        ...

    def test_is_file_retruns_true_if_file(self):
        ...

    def test_is_file_returns_false_if_directory(self):
        ...

    def test_is_file_returns_false_if_symlink(self):
        ...


class TestGitTree:
    def test_entries_returns_all_entries(self):
        ...

    def test_files_returns_only_file_entries(self):
        ...
