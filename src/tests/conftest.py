from unittest.mock import AsyncMock

import pytest_asyncio

from project.api.base import BaseRepositoryBranchApi


@pytest_asyncio.fixture
def mock_api():
    api = AsyncMock(spec=BaseRepositoryBranchApi)
    return api
