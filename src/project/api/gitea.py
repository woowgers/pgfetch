from base64 import b64decode
from collections.abc import Sequence
from http import HTTPStatus
from pathlib import Path

import aiohttp
import requests

from project.api.base import BaseRepositoryBranch, BaseRepositoryBranchApi
from project.models import GitBranch, GitEntry, GitTree


class GiteaRepositoryBranch(BaseRepositoryBranch):
    @property
    def base_url(self) -> str:
        return f"https://{self.host}/api/v1"

    def get_branches_list_url(self) -> str:
        return f"{self.base_url}/repos/{self.org}/{self.repo}/branches"

    def get_branch_tree_url(self, branch_id: str) -> str:
        return f"{self.base_url}/repos/{self.org}/{self.repo}/git/trees/{branch_id}?recursive=true"

    def get_filepath_content_url(self, filepath: Path) -> str:
        return f"{self.base_url}/repos/{self.org}/{self.repo}/contents/{filepath}?ref={self.name}"


class GiteaRepositoryBranchApi(BaseRepositoryBranchApi):
    def __init__(self, session: aiohttp.ClientSession, branch: GiteaRepositoryBranch):
        self.session = session
        self.branch = branch

    def get_branch_id(self) -> str:
        url = self.branch.get_branches_list_url()

        response = requests.get(url)
        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f"Failed to retrieve branch {self.branch}")

        branches = tuple(self.construct_gitbranch(raw_branch) for raw_branch in response.json())
        return self._find_branch_by_name(branches).id

    async def get_branch_tree(self) -> GitTree:
        branch_id = self.get_branch_id()
        url = self.branch.get_branch_tree_url(branch_id)

        async with self.session.get(url) as response:
            if response.status != HTTPStatus.OK:
                raise RuntimeError(f"Failed to retrieve branch {self.branch} filepaths")

            return self.construct_gittree(await response.json())

    async def get_file_content(self, filepath: Path) -> str:
        url = self.branch.get_filepath_content_url(filepath)

        async with self.session.get(url) as response:
            if response.status != HTTPStatus.OK:
                raise RuntimeError(f"Failed to retrieve file {filepath}")

            return self._get_text_from_raw_content_response(await response.json())

    def construct_gitentry(self, raw_entry: dict) -> GitEntry:
        return GitEntry(path=raw_entry["path"], is_file=raw_entry["type"] == "blob")

    def construct_gittree(self, raw_tree: dict) -> GitTree:
        entries = tuple(self.construct_gitentry(raw_entry) for raw_entry in raw_tree["tree"])
        return GitTree(entries=entries)

    def construct_gitbranch(self, raw_branch: dict) -> GitBranch:
        return GitBranch(raw_branch["name"], raw_branch["commit"]["id"])

    def _get_text_from_raw_content_response(self, raw_content_response: dict) -> str:
        raw_content = raw_content_response["content"]
        return b64decode(raw_content.encode()).decode()

    def _find_branch_by_name(self, branches: Sequence[GitBranch]) -> GitBranch:
        for branch in branches:
            if branch.name == self.branch.name:
                return branch

        raise ValueError(f"No branch {self.branch} in repository")
