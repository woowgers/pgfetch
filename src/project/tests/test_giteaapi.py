from pathlib import Path
from typing import Sequence
from unittest.mock import patch

import pytest

from project.giteaapi import GiteaRepositoryBranchApi
from project.tests.conftest import JSON, MockAsyncResponse, MockResponse
from project.types import GitBranch, GitEntry, GitTree


def test_branch_list_url(api: GiteaRepositoryBranchApi, expected_branches_list_url: str):
    assert api._branches_list_url() == expected_branches_list_url


def test_branch_tree_url(api: GiteaRepositoryBranchApi, expected_branch: GitBranch, expected_branch_tree_url: str):
    with patch("project.giteaapi.GiteaRepositoryBranchApi.get_branch_id") as get_branch_id:
        get_branch_id.return_value = expected_branch.id
        assert api._branch_tree_url() == expected_branch_tree_url


def test_file_content_url(api: GiteaRepositoryBranchApi, file_entry: GitEntry, expected_file_content_url: str):
    assert api._file_content_url(file_entry.path) == expected_file_content_url


@pytest.mark.skip
class TestGetBranchByNameOrValueError:
    @pytest.fixture
    def expected_valueerror(self, expected_branch: GitBranch) -> ValueError:
        return ValueError(f"No branch {expected_branch.name} in repository")

    def test_raises_expected_valueerror_if_no_given_branch(
        self, api: GiteaRepositoryBranchApi, branches_without_expected_branch: Sequence[GitBranch]
    ):
        with pytest.raises(ValueError):
            api.get_branch_by_name_or_valueerror(branches_without_expected_branch)

    def test_returns_expected_branch_if_given(
        self, api: GiteaRepositoryBranchApi, expected_branches: Sequence[GitBranch], expected_branch: GitBranch
    ):
        assert api.get_branch_by_name_or_valueerror(expected_branches) == expected_branch


@pytest.mark.skip
class TestGetBranchId:
    @pytest.fixture
    def expected_runtimeerror(self, expected_branch: GitBranch) -> RuntimeError:
        return RuntimeError(f"skiped to retrieve branch {expected_branch.name}")

    def test_raises_runtimeerror_if_response_status_not_200(
        self, api: GiteaRepositoryBranchApi, raw_branches: JSON, expected_runtimeerror: RuntimeError
    ):
        with patch("requests.get") as get:
            get.return_value = MockResponse(404, raw_branches)

            with pytest.raises(RuntimeError) as error:
                api.get_branch_id()

            assert str(error.value) == str(expected_runtimeerror)

    def test_returns_id(self, api: GiteaRepositoryBranchApi, raw_branches: JSON, expected_branch: GitBranch):
        with patch("requests.get") as get:
            get.return_value = MockResponse(200, raw_branches)
            branch_id = api.get_branch_id()
            assert branch_id == expected_branch.id


@pytest.mark.skip
class TestGetBranchTree:
    @pytest.fixture
    def expected_runtimeerror(self, expected_branch: GitBranch) -> RuntimeError:
        return RuntimeError(f"skiped to retrieve branch {expected_branch.name} filepaths")

    @pytest.mark.asyncio
    async def test_raises_runtimeerror_if_response_status_not_200(
        self, api: GiteaRepositoryBranchApi, expected_runtimeerror: RuntimeError, expected_branch: GitBranch
    ):
        ...

    @pytest.mark.asyncio
    async def test_returns_expected_tree(
        self, api: GiteaRepositoryBranchApi, expected_raw_tree: dict, expected_tree: GitTree
    ):
        ...


class TestGetFileContent:
    ...
