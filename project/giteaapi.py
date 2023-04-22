from base64 import b64decode
from http import HTTPStatus
from pathlib import Path
from typing import Self, Sequence

import aiohttp
import requests

from project.types import GitBranch, GitTree


class GiteaRepositoryBranchApi:
    def __init__(self, host: str, org: str, repo: str, branch: str):
        self.base_url: str = f"https://{host}/api/v1"
        self.repo: str = repo
        self.org: str = org
        self.branch: str = branch
        self.session = aiohttp.ClientSession()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_) -> None:
        await self.session.close()

    def _branch_list_url(self) -> str:
        return self.base_url + f"/repos/{self.org}/{self.repo}/branches"

    def _branch_tree_url(self) -> str:
        branch_id = self.get_branch_id()
        return self.base_url + f"/repos/{self.org}/{self.repo}/git/trees/{branch_id}?recursive=true"

    def _file_content_url(self, filepath: Path):
        return f"{self.base_url}/repos/{self.org}/{self.repo}/contents/{filepath}?ref={self.branch}"

    def get_branch_by_name_or_valueerror(self, branches: Sequence[GitBranch]) -> GitBranch:
        for branch in branches:
            if branch.name == self.branch:
                return branch

        raise ValueError(f"No branch {self.branch} in repository")

    def get_branch_id(self) -> str:
        url = self._branch_list_url()

        response = requests.get(url)
        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f"Failed to retrieve branch {self.branch}")

        branches = tuple(GitBranch.parse_from_raw(raw_branch) for raw_branch in response.json())
        return self.get_branch_by_name_or_valueerror(branches).id

    async def get_branch_tree(self) -> GitTree:
        url = self._branch_tree_url()

        async with self.session.get(url) as response:
            if response.status != 200:
                raise RuntimeError(f"Failed to retrieve branch {self.branch} filepaths")

            return GitTree(await response.json())

    def get_file_text_from_raw_content(self, raw_content: str) -> str:
        return b64decode(raw_content.encode()).decode()

    async def get_file_content(self, filepath: Path) -> str:
        url = self._file_content_url(filepath)

        async with self.session.get(url) as response:
            if response.status != 200:
                raise RuntimeError(f"Failed to retrieve file {filepath}")

            return self.get_file_text_from_raw_content(await response.json())
