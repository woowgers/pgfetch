from pathlib import Path
from typing import Protocol

from project.models import GitTree


class BaseRepositoryBranchApi(Protocol):
    def _branches_list_url(self) -> str:
        ...

    def _branch_tree_url(self) -> str:
        ...

    def _file_content_url(self, filepath: Path) -> str:
        ...

    def get_branch_id(self) -> str:
        ...

    async def get_branch_tree(self) -> GitTree:
        ...

    async def get_file_content(self, filepath: Path) -> str:
        ...

