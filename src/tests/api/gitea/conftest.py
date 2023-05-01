from collections.abc import Callable
from pathlib import Path
from unittest.mock import AsyncMock

import aiohttp
import pytest

from project.api.gitea import GiteaRepositoryBranch, GiteaRepositoryBranchApi

host = 'host'
repo = 'repo'
org = 'org'
name = 'name'
base_url = f"https://{host}/api/v1"


@pytest.fixture
def mock_session() -> aiohttp.ClientSession:
    return AsyncMock(side_effect=aiohttp.ClientSession)


@pytest.fixture
def branch() -> GiteaRepositoryBranch:
    return GiteaRepositoryBranch(host=host, repo=repo, org=org, name=name)


@pytest.fixture
def api(branch: GiteaRepositoryBranch, mock_session: aiohttp.ClientSession) -> GiteaRepositoryBranchApi:
    return GiteaRepositoryBranchApi(branch=branch, session=mock_session)


@pytest.fixture
def expected_base_url() -> str:
    return base_url


@pytest.fixture
def expected_branches_list_url() -> str:
    return f"{base_url}/repos/{org}/{repo}/branches"


@pytest.fixture
def expected_branch_tree_url() -> Callable[[str], str]:
    def _expected_branch_tree_url(branch_id: str) -> str:
        return f"{base_url}/repos/{org}/{repo}/git/trees/{branch_id}?recursive=true"

    return _expected_branch_tree_url


@pytest.fixture
def expected_filepath_content_url() -> Callable[[Path], str]:
    def _expected_filepath_content_url(filepath: Path) -> str:
        return f"{base_url}/repos/{org}/{repo}/contents/{filepath}?ref={name}"

    return _expected_filepath_content_url
