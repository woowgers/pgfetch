from pathlib import Path

import aiohttp
import requests

from project.types import FileContent, GitBranch, GitTree


class GiteaRepositoryBranchApi:
    def __init__(self, host: str, org: str, repo: str, branch: str):
        self.base_url: str = f"https://{host}/api/v1"
        self.repo: str = repo
        self.org: str = org
        self.branch: str = branch

    def get_branch_id_sync(self) -> str:
        url = self.base_url + f"/repos/{self.org}/{self.repo}/branches"

        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to retrieve branch {self.branch}")

        branches = map(GitBranch, response.json())
        for branch in branches:
            if branch.name == self.branch:
                return branch.id

        raise ValueError(f"No branch {self.branch} in repository")

    async def get_branch_tree(self) -> GitTree:
        branch_id = self.get_branch_id_sync()
        url = self.base_url + f"/repos/{self.org}/{self.repo}/git/trees/{branch_id}?recursive=true"

        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                raise RuntimeError(f"Failed to retrieve branch {self.branch} filepaths")

            return GitTree(await response.json())

    async def get_file_content(self, filepath: str | Path) -> FileContent:
        url = self.base_url + f"/repos/{self.org}/{self.repo}/contents/{filepath}?ref={self.branch}"

        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                raise RuntimeError(f"Failed to retrieve file {filepath}")

            return FileContent(await response.json())
