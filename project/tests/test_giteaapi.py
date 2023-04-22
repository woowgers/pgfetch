from unittest.mock import patch

import pytest

from project.giteaapi import GiteaRepositoryBranchApi
from project.types import GitBranch, GitTree

from project.tests.conftest import JSON, MockAsyncResponse, MockResponse


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
    ...
