from base64 import b64decode

import aiohttp
import requests


class GiteaRepositoryApi:
    def __init__(self, host: str, org: str, repo: str):
        self.base_url: str = f"https://{host}/api/v1"
        self.repo: str = repo
        self.org: str = org

    def get_branch_id(self, branch: str) -> str:
        url = self.base_url + f"/repos/{self.org}/{self.repo}/branches"
        raw_branches = requests.get(url).json()
        for raw_branch in raw_branches:
            if raw_branch["name"] == branch:
                return raw_branch["commit"]["id"]

        raise ValueError(f"No branch {branch} in repository")

    def get_branch_filepaths(self, branch_id: str) -> tuple[str, ...]:
        def gitentry_path_is_regular_file(raw_gitentry: dict) -> bool:
            return raw_gitentry["type"] == "blob"

        url = self.base_url + f"/repos/{self.org}/{self.repo}/git/trees/{branch_id}?recursive=true"
        raw_tree = requests.get(url).json()
        filepaths = tuple(gitentry["path"] for gitentry in raw_tree["tree"] if gitentry_path_is_regular_file(gitentry))

        return filepaths

    async def get_file_content(self, filepath: str) -> bytes:
        url = self.base_url + f"/repos/{self.org}/{self.repo}/contents/{filepath}"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            return b64decode((await response.json())["content"])
