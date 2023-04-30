from unittest.mock import AsyncMock
import pytest_asyncio

from project.giteaapi import BaseRepositoryBranchApi


@pytest_asyncio.fixture
def mock_api():
    api = AsyncMock(spec=BaseRepositoryBranchApi)
    return api
