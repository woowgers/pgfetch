from base64 import b64encode
from pathlib import Path
from typing import Sequence, TypeAlias
from unittest.mock import patch

import pytest

from project.giteaapi import GiteaRepositoryBranchApi
from project.types import FileContent, GitBranch, GitTree

pytest_plugins = "pytest_asyncio"


JSON: TypeAlias = dict | Sequence[dict]


class MockResponse:
    def __init__(self, status_code: int, json: JSON | None = None):
        self.status_code: int = status_code
        self._json: JSON = json or dict()

    def json(self) -> JSON:
        return self._json


class MockAsyncResponse:
    def __init__(self, status_code: int, json: JSON | None = None):
        self.status_code: int = status_code
        self._json: JSON = json or dict()

    @property
    def status(self) -> int:
        return self.status_code

    async def json(self) -> JSON:
        return self._json

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass


@pytest.fixture
def api() -> GiteaRepositoryBranchApi:
    return GiteaRepositoryBranchApi("host", "org", "repo", "master")


@pytest.fixture
def raw_expected_branch() -> JSON:
    return {"name": "master", "commit": {"id": "jf2j30923jfaij903f"}}


@pytest.fixture
def raw_unexpected_branch() -> JSON:
    return {"name": "dev", "commit": {"id": "soifj0jf209jf02j93f"}}


@pytest.fixture
def expected_branch(raw_expected_branch: dict) -> GitBranch:
    return GitBranch(raw_expected_branch)


@pytest.fixture
def raw_branches(raw_expected_branch: dict, raw_unexpected_branch: dict) -> JSON:
    return (raw_expected_branch, raw_unexpected_branch)


@pytest.fixture
def raw_branches_without_expected_branch(raw_unexpected_branch: dict) -> JSON:
    return (raw_unexpected_branch,)


@pytest.fixture
def expected_raw_tree() -> dict:
    return {"tree": ({"path": "/path/to/some/file", "type": "blob"}, {"path": "/path/to/a/directory", "type": "tree"})}

@pytest.fixture
def expected_tree(expected_raw_tree: dict) -> GitTree:
    return GitTree(expected_raw_tree)

@pytest.fixture
def expected_raw_content() -> dict:
    return {
        "content": b64encode("some content".encode()).decode()
    }

@pytest.fixture
def expected_content(expected_raw_content: dict) -> FileContent:
    return FileContent(expected_raw_content)

@pytest.fixture
def expected_filepath() -> Path:
    return Path("/some/path/to/a/file/or/directory")


class TestGetBranchIdSync:
    @pytest.fixture
    def expected_runtimeerror(self, expected_branch: GitBranch) -> RuntimeError:
        return RuntimeError(f"Failed to retrieve branch {expected_branch.name}")

    @pytest.fixture
    def expected_valueerror(self, expected_branch: GitBranch) -> RuntimeError:
        return RuntimeError(f"No branch {expected_branch.name} in repository")

    def test_raises_runtimeerror_if_response_status_not_200(
        self, api: GiteaRepositoryBranchApi, raw_branches: JSON, expected_runtimeerror: RuntimeError
    ):
        with patch("requests.get") as get:
            get.return_value = MockResponse(404, raw_branches)

            with pytest.raises(RuntimeError) as error:
                api.get_branch_id()

            assert str(error.value) == str(expected_runtimeerror)

    def test_raises_valueerror_if_branch_not_in_repo(
        self, api: GiteaRepositoryBranchApi, raw_branches_without_expected_branch: dict, expected_valueerror: ValueError
    ):
        with patch("requests.get") as get:
            get.return_value = MockResponse(200, raw_branches_without_expected_branch)

            with pytest.raises(ValueError) as error:
                api.get_branch_id()

            assert str(error.value) == str(expected_valueerror)

    def test_returns_id(self, api: GiteaRepositoryBranchApi, raw_branches: JSON, expected_branch: GitBranch):
        with patch("requests.get") as get:
            get.return_value = MockResponse(200, raw_branches)
            branch_id = api.get_branch_id()
            assert branch_id == expected_branch.id


class TestGetBranchTree:
    @pytest.fixture
    def expected_runtimeerror(self, expected_branch: GitBranch) -> RuntimeError:
        return RuntimeError(f"Failed to retrieve branch {expected_branch.name} filepaths")

    @pytest.mark.asyncio
    async def test_raises_runtimeerror_if_response_status_not_200(
        self, api: GiteaRepositoryBranchApi, expected_runtimeerror: RuntimeError, expected_branch: GitBranch
    ):
        with (
            patch("project.giteaapi.GiteaRepositoryApi.get_branch_id_sync") as branch_id,
            patch("aiohttp.ClientSession.get") as get,
        ):
            branch_id.return_value = expected_branch.id
            branch_id.return_value = expected_branch.id
            get.return_value = MockAsyncResponse(404)

            with pytest.raises(RuntimeError) as error:
                await api.get_branch_tree()

            assert str(error.value) == str(expected_runtimeerror)

    @pytest.mark.asyncio
    async def test_returns_expected_tree(
        self, api: GiteaRepositoryBranchApi, expected_branch: GitBranch, expected_raw_tree: dict, expected_tree: GitTree
    ):
        with (
            patch("project.giteaapi.GiteaRepositoryApi.get_branch_id_sync") as branch_id,
            patch("aiohttp.ClientSession.get") as get,
        ):
            branch_id.return_value = expected_branch.id
            get.return_value = MockAsyncResponse(200, expected_raw_tree)
            tree = await api.get_branch_tree()
            assert tree == expected_tree


class TestGetFileContent:
    @pytest.fixture
    def expected_runtimeerror(self, expected_filepath: Path) -> RuntimeError:
        return RuntimeError(f"Failed to retrieve file {expected_filepath}")

    @pytest.mark.asyncio
    async def test_raises_runtimeerror_if_response_status_not_200(
        self, api: GiteaRepositoryBranchApi, expected_filepath: Path, expected_runtimeerror: RuntimeError
    ):
        with patch("aiohttp.ClientSession.get") as get:
            get.return_value = MockAsyncResponse(404)
            with pytest.raises(RuntimeError) as error:
                await api.get_file_content(expected_filepath)
            assert str(error.value) == str(expected_runtimeerror)

    @pytest.mark.asyncio
    async def test_returns_expected_content(self, api: GiteaRepositoryBranchApi, expected_raw_content: JSON, expected_content: FileContent):
        with patch("aiohttp.ClientSession.get") as get:
            get.return_value = MockAsyncResponse(200, expected_raw_content)
            content = await api.get_file_content('filename')
            assert content == expected_content
