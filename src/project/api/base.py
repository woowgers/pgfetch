from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from project.models import GitBranch, GitEntry, GitTree


@dataclass
class BaseRepositoryBranch(ABC):
    host: str
    repo: str
    org: str
    name: str

    @abstractproperty
    def base_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_branches_list_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_branch_tree_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_filepath_content_url(self) -> str:
        raise NotImplementedError


class BaseRepositoryBranchApi(Protocol):
    def get_branch_id(self) -> str:
        ...

    async def get_branch_tree(self) -> GitTree:
        ...

    async def get_file_content(self, filepath: Path) -> str:
        ...

    def construct_gitentry(self, raw_entry: dict) -> GitEntry:
        ...

    def construct_gittree(self, raw_tree: dict) -> GitTree:
        ...

    def construct_gitbranch(self, raw_branch: dict) -> GitBranch:
        ...
